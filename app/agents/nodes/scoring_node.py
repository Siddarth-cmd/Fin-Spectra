from ..state import InvestigationState
from ...database import SessionLocal
from ...models.schema import InvestigationCase

def scoring_node(state: InvestigationState) -> InvestigationState:
    """
    Phase 12 & 13: Transparent Risk Engine & Explainable Decision
    Derives risk score reproducibly from factual findings with explicit factor values, weights, and contributions.
    """
    behavior = state.get("behavioral_metrics") or {}
    graph = state.get("graph_metrics") or {}
    kyc = state.get("kyc_metrics") or {}
    typology_ev = state.get("detected_typology_evidence") or {}
    customer = (state.get("trigger_evidence") or {}).get("customer") or {}

    factors = []

    # 1. Behavior Anomaly (Z-Score & Velocity)
    z_score = float(behavior.get("velocity_z_score", 0.0))
    b_val = min(z_score * 20.0, 100.0)
    b_contrib = 0.25 * b_val
    factors.append({
        "factor_name": "Behavioral Velocity Anomaly (Z-Score)",
        "factor_value": f"Z-Score = {z_score:.2f}σ",
        "weight": 0.25,
        "raw_score": round(b_val, 1),
        "contribution": round(b_contrib, 2),
        "source": "ledger_history"
    })

    # 2. KYC Income Activity Ratio Mismatch
    ratio = float(kyc.get("income_activity_ratio", 1.0))
    k_val = min(ratio * 25.0, 100.0) if ratio > 1.0 else 10.0
    k_contrib = 0.20 * k_val
    factors.append({
        "factor_name": "KYC Income Activity Mismatch",
        "factor_value": f"Turnover/Income Ratio = {ratio:.2f}x",
        "weight": 0.20,
        "raw_score": round(k_val, 1),
        "contribution": round(k_contrib, 2),
        "source": "customers"
    })

    # 3. Typology Detection Severity
    t_val = 0.0
    if "STRUCTURING" in typology_ev:
        t_val += 40.0
    if "RAPID_PASS_THROUGH" in typology_ev:
        t_val += 45.0
    if "CIRCULAR_FLOW" in typology_ev:
        t_val += 50.0
    if "FAN_IN" in typology_ev or "FAN_OUT" in typology_ev:
        t_val += 30.0
    t_val = min(t_val, 100.0) if t_val > 0 else 15.0
    t_contrib = 0.30 * t_val
    factors.append({
        "factor_name": "Transaction Typology Severity",
        "factor_value": f"Detected: {state.get('typology_classification', 'UNKNOWN')}",
        "weight": 0.30,
        "raw_score": round(t_val, 1),
        "contribution": round(t_contrib, 2),
        "source": "detected_typology_evidence"
    })

    # 4. Graph Network Topology Risk
    g_val = 0.0
    if graph.get("cycles_detected"):
        g_val += 50.0
    if graph.get("target_out_degree", 0) >= 2 or graph.get("target_in_degree", 0) >= 2:
        g_val += 35.0
    g_val = min(g_val, 100.0) if g_val > 0 else 10.0
    g_contrib = 0.25 * g_val
    factors.append({
        "factor_name": "Graph Network Topology Risk",
        "factor_value": f"Cycles: {graph.get('cycles_detected')}, In/Out Deg: {graph.get('target_in_degree',0)}/{graph.get('target_out_degree',0)}",
        "weight": 0.25,
        "raw_score": round(g_val, 1),
        "contribution": round(g_contrib, 2),
        "source": "transactions (NetworkX graph)"
    })

    final_score = round(sum(f["contribution"] for f in factors), 2)
    final_score = min(max(final_score, 0.0), 100.0)

    state["final_risk_score"] = final_score

    if final_score <= 40.0:
        decision = "ALLOW"
    elif final_score <= 75.0:
        decision = "REVIEW"
    else:
        decision = "BLOCK"

    state["decision"] = decision
    state["risk_factors_breakdown"] = factors
    state["risk_subscores"] = {
        "kyc": round(k_val, 1),
        "behavior": round(b_val, 1),
        "graph": round(g_val, 1),
        "typology": round(t_val, 1),
    }

    # Detailed Explainable Findings
    state["explainable_findings"] = {
        "summary": f"Alert scored {final_score}/100 resulting in {decision} verdict.",
        "primary_typology": state.get("typology_classification", "UNKNOWN"),
        "key_evidence": [
            f"Behavior: {factors[0]['factor_value']} (Contrib: {factors[0]['contribution']} pts)",
            f"KYC: {factors[1]['factor_value']} (Contrib: {factors[1]['contribution']} pts)",
            f"Typology: {factors[2]['factor_value']} (Contrib: {factors[2]['contribution']} pts)",
            f"Graph Topology: {factors[3]['factor_value']} (Contrib: {factors[3]['contribution']} pts)"
        ],
        "recommended_next_action": "File Suspicious Activity Report (SAR) with FIU" if decision == "BLOCK" else "Perform enhanced due diligence"
    }

    # Persist case to DB
    db = SessionLocal()
    try:
        case = db.query(InvestigationCase).filter(InvestigationCase.id == state["case_id"]).first()
        if not case:
            case = InvestigationCase(
                id=state["case_id"],
                alert_id=state["alert_id"],
                entity_id=state["entity_id"],
                priority_score=final_score,
                priority_band="CRITICAL" if final_score > 85 else ("HIGH" if final_score > 70 else "MEDIUM"),
                status="CLOSED"
            )
            db.add(case)

        case.final_risk_score = final_score
        case.decision = decision
        case.state_snapshot_json = dict(state)
        case.status = "CLOSED"
        db.commit()
    except Exception as err:
        db.rollback()
        raise err
    finally:
        db.close()

    return state
