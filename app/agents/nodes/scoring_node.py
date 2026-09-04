from ..state import InvestigationState
from ...database import SessionLocal
from ...models.schema import InvestigationCase

def scoring_node(state: InvestigationState) -> InvestigationState:
    """
    Weighted Multi-Factor Composite Scoring Model:
    Final = 0.35 * Phase1 + 0.25 * Behavior + 0.25 * Graph + 0.15 * KYC
    
    Thresholds:
    - <= 40.0: ALLOW
    - <= 75.0: REVIEW
    - > 75.0:  BLOCK
    """
    trigger_evidence = state.get("trigger_evidence", {})
    customer = trigger_evidence.get("customer") or {}

    # 1. Phase 1 Prior Sub-Score (0-100)
    phase1_score = min(max(float(state.get("raw_priority_score", 0.0)), 0.0), 100.0)

    # 2. Behavioral Sub-Score (0-100)
    behavior = state.get("behavioral_metrics", {})
    z_score = float(behavior.get("velocity_z_score", 0.0))
    pass_through = float(behavior.get("pass_through_ratio", 0.0))

    if z_score > 3.0:
        behavior_base = 100.0
    elif z_score > 1.5:
        behavior_base = 60.0
    else:
        behavior_base = 10.0

    if pass_through > 0.9:
        behavior_base += 20.0

    behavior_score = min(behavior_base, 100.0)

    # 3. Graph Network Sub-Score (0-100)
    graph = state.get("graph_metrics", {})
    graph_base = 0.0

    if graph.get("self_transfer_detected") or graph.get("circular_paths_detected"):
        graph_base += 50.0

    if graph.get("multi_device_multi_beneficiary_flag") or graph.get("shell_intermediaries_suspected"):
        graph_base += 30.0

    dispersion = float(graph.get("beneficiary_dispersion_ratio", 0.0))
    if dispersion > 0.7:
        graph_base += 20.0

    graph_score = min(graph_base, 100.0)

    # 4. KYC Sub-Score (0-100)
    kyc_base = 0.0
    risk_level = str(customer.get("risk_level", "LOW")).upper()
    if risk_level == "HIGH":
        kyc_base += 50.0
    elif risk_level == "MEDIUM":
        kyc_base += 25.0

    acc_age = int(customer.get("account_age_days", 999))
    if acc_age < 180:
        kyc_base += 20.0

    kyc_notes = state.get("kyc_notes", "")
    if "ALERT" in kyc_notes:
        kyc_base += 30.0

    kyc_score = min(kyc_base, 100.0)

    # 5. Composite Final Score & Decision Thresholds
    final_score = round(
        (0.35 * phase1_score) +
        (0.25 * behavior_score) +
        (0.25 * graph_score) +
        (0.15 * kyc_score),
        2
    )
    final_score = min(final_score, 100.0)
    state["final_risk_score"] = final_score

    if final_score <= 40.0:
        decision = "ALLOW"
    elif final_score <= 75.0:
        decision = "REVIEW"
    else:
        decision = "BLOCK"

    state["decision"] = decision

    # Subscore dictionary & concise explanation
    subscores = {
        "phase1_prior": phase1_score,
        "behavior": behavior_score,
        "graph": graph_score,
        "kyc": kyc_score
    }
    explanation = (
        f"Composite Score: {final_score}/100 -> Decision: {decision}. "
        f"Breakdown: Phase1 Prior ({phase1_score:.1f} x 35%), "
        f"Behavior ({behavior_score:.1f} x 25%), "
        f"Graph ({graph_score:.1f} x 25%), "
        f"KYC ({kyc_score:.1f} x 15%)."
    )

    # Store subscores and explanation in state
    state["behavioral_metrics"]["risk_subscores"] = subscores
    state["behavioral_metrics"]["risk_explanation"] = explanation

    # Persist final state snapshot to Neon PostgreSQL
    db = SessionLocal()
    try:
        case = db.query(InvestigationCase).filter(InvestigationCase.id == state["case_id"]).first()
        if not case:
            case = InvestigationCase(
                id=state["case_id"],
                alert_id=state["alert_id"],
                entity_id=state["entity_id"],
                priority_score=phase1_score,
                priority_band="HIGH" if phase1_score > 70 else "MEDIUM",
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
