from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.schema import ClassifiedAlert, InvestigationCase
from ..agents.graph import investigation_graph
import uuid

router = APIRouter()

@router.post("/run")
def run_investigation(alert: ClassifiedAlert, db: Session = Depends(get_db)):
    """
    The Connection Bridge entry point.
    Accepts a ClassifiedAlert from Phase 1 and runs the LangGraph multi-agent investigation.
    """
    alert_id = alert.get_alert_id()
    entity_id = alert.get_entity_id()
    severity = alert.get_severity()
    raw_score = alert.get_score()
    trigger_evidence = alert.get_features()

    case_id = f"CASE_{alert_id}"

    # Check if already investigated
    existing = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if existing:
        return {"status": "already_investigated", "case_id": case_id, "decision": existing.decision, "score": existing.final_risk_score}

    # Create case record
    case = InvestigationCase(
        id=case_id,
        alert_id=alert_id,
        entity_id=entity_id,
        priority_score=raw_score,
        priority_band=severity,
        status="OPEN"
    )
    db.add(case)
    db.commit()

    # Seed the LangGraph initial state
    initial_state = {
        "case_id": case_id,
        "alert_id": alert_id,
        "entity_id": entity_id,
        "alert_type": alert.alert_type,
        "raw_priority_score": raw_score,
        "trigger_evidence": trigger_evidence,
        "task_list": [],
        "current_task": "",
        "plan_satisfied": False,
        "loop_count": 0,
        "missing_evidence": [],
        "historical_cases": [],
        "ledger_history": [],
        "balance_history": {},
        "behavioral_metrics": {},
        "graph_metrics": {},
        "kyc_notes": "",
        "typology_classification": "",
        "typology_rationale": "",
        "forensic_questions": [],
        "investigation_plan": [],
        "dossier": "",
        "final_risk_score": 0.0,
        "decision": ""
    }

    # Run the graph with thread_id = case_id (LangGraph state memory)
    config = {"configurable": {"thread_id": case_id}}
    final_state = investigation_graph.invoke(initial_state, config=config)

    return {
        "status": "plan_check_completed",
        "case_id": case_id,
        "entity_id": alert.entity_id,
        "plan_satisfied": final_state.get("plan_satisfied", False),
        "task_list": final_state.get("task_list", []),
        "investigation_plan": final_state.get("investigation_plan", []),
        "missing_evidence": final_state.get("missing_evidence", []),
        "collected_evidence_summary": {
            "ledger_records": len(final_state.get("ledger_history", [])),
            "kyc_notes": final_state.get("kyc_notes", ""),
            "behavioral_metrics": final_state.get("behavioral_metrics", {}),
            "graph_metrics": final_state.get("graph_metrics", {})
        }
    }

@router.get("/cases")
def list_cases(db: Session = Depends(get_db)):
    cases = db.query(InvestigationCase).order_by(InvestigationCase.created_at.desc()).limit(50).all()
    return [{"id": c.id, "alert_id": c.alert_id, "entity_id": c.entity_id, "decision": c.decision, "score": c.final_risk_score, "status": c.status} for c in cases]

@router.get("/cases/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"id": case.id, "decision": case.decision, "score": case.final_risk_score, "state": case.state_snapshot_json}


@router.get("/cases/{case_id}/detail")
def get_case_detail(case_id: str, db: Session = Depends(get_db)):
    """
    Full investigation workspace payload for the frontend investigation view.
    Returns structured state snapshot with all agent evidence, risk scores, and dossier.
    """
    case = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    state = case.state_snapshot_json or {}
    behavioral = state.get("behavioral_metrics") or {}
    graph = state.get("graph_metrics") or {}
    subscores = state.get("risk_subscores") or behavioral.get("risk_subscores") or {}

    # Extract KYC subscore with fallback to risk factors breakdown or kyc_metrics
    kyc_score = float(subscores.get("kyc", 0.0))
    if kyc_score == 0.0:
        factors = state.get("risk_factors_breakdown") or []
        for f in factors:
            if "KYC" in f.get("factor_name", "").upper():
                kyc_score = float(f.get("raw_score", 0.0))
                break
        if kyc_score == 0.0:
            kyc_metrics = state.get("kyc_metrics") or {}
            ratio = float(kyc_metrics.get("income_activity_ratio", 1.0))
            kyc_score = min(ratio * 25.0, 100.0) if ratio > 1.0 else 10.0

    # Extract Behavior subscore with fallback
    behavior_score = float(subscores.get("behavior", 0.0))
    if behavior_score == 0.0:
        z_score = float(behavioral.get("velocity_z_score", 0.0))
        behavior_score = min(z_score * 20.0, 100.0) if z_score > 0 else 0.0

    # Extract Graph subscore with fallback
    graph_score = float(subscores.get("graph", 0.0))
    if graph_score == 0.0:
        factors = state.get("risk_factors_breakdown") or []
        for f in factors:
            if "GRAPH" in f.get("factor_name", "").upper():
                graph_score = float(f.get("raw_score", 0.0))
                break

    # Build structured task list with agent mapping
    task_list = state.get("task_list") or []
    agent_map = {
        "FETCH_EVIDENCE": "Evidence Retrieval",
        "VERIFY_KYC": "KYC Verifier",
        "ANALYZE_BEHAVIOR": "Behavioral Analyzer",
        "ANALYZE_GRAPH": "Graph Analyst",
    }
    tasks_display = [
        {
            "task_id": t.get("task_id"),
            "name": t.get("name"),
            "agent_label": agent_map.get(t.get("name", ""), t.get("name", "")),
            "status": t.get("status"),
            "required_evidence_key": t.get("required_evidence_key"),
        }
        for t in task_list
    ]

    # Transaction ledger from state
    ledger = state.get("ledger_history") or []

    return {
        "case_id": case.id,
        "alert_id": case.alert_id,
        "entity_id": case.entity_id,
        "status": case.status,
        "priority_score": case.priority_score,
        "priority_band": case.priority_band,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "updated_at": case.updated_at.isoformat() if case.updated_at else None,

        # Final outputs
        "final_risk_score": case.final_risk_score,
        "decision": case.decision,

        # Plan & tasks
        "investigation_plan": state.get("investigation_plan") or [],
        "task_list": tasks_display,
        "plan_satisfied": state.get("plan_satisfied", False),
        "missing_evidence": state.get("missing_evidence") or [],
        "loop_count": state.get("loop_count", 0),

        # Typology
        "typology_classification": state.get("typology_classification", ""),
        "typology_rationale": state.get("typology_rationale", ""),
        "alert_type": state.get("alert_type", ""),

        # Evidence summary
        "evidence_summary": {
            "ledger_count": len(ledger),
            "ledger_history": ledger,
            "kyc_notes": state.get("kyc_notes", ""),
            "balance_history": state.get("balance_history") or {},
            "historical_cases_count": len(state.get("historical_cases") or []),
        },

        # Behavioral metrics
        "behavioral_metrics": {
            "velocity_z_score": behavioral.get("velocity_z_score", 0.0),
            "pass_through_ratio": behavioral.get("pass_through_ratio", 0.0),
            "total_volume_in": behavioral.get("total_volume_in", 0.0),
            "total_volume_out": behavioral.get("total_volume_out", 0.0),
            "trigger_amount": behavioral.get("trigger_amount", 0.0),
            "historical_mean": behavioral.get("historical_mean", 0.0),
            "historical_stddev": behavioral.get("historical_stddev", 0.0),
            "effective_stddev": behavioral.get("effective_stddev", 0.0),
            "historical_transaction_count": behavioral.get("historical_transaction_count", 0),
            "velocity_baseline_status": behavioral.get("velocity_baseline_status", ""),
            "risk_explanation": behavioral.get("risk_explanation", ""),
        },

        # Graph metrics
        "graph_metrics": {
            "account_count": graph.get("account_count", 0),
            "beneficiary_count": graph.get("beneficiary_count", 0),
            "device_count": graph.get("device_count", 0),
            "transaction_count": graph.get("transaction_count", 0),
            "unique_beneficiaries": graph.get("unique_beneficiaries", 0),
            "tx_per_account": graph.get("tx_per_account", 0.0),
            "beneficiary_dispersion_ratio": graph.get("beneficiary_dispersion_ratio", 0.0),
            "multi_beneficiary_flag": graph.get("multi_beneficiary_flag", 0),
            "multi_device_multi_beneficiary_flag": graph.get("multi_device_multi_beneficiary_flag", False),
            "self_transfer_detected": graph.get("self_transfer_detected", False),
            "fan_in_ratio": graph.get("fan_in_ratio", 0.0),
            "fan_out_ratio": graph.get("fan_out_ratio", 0.0),
        },

        # Risk scoring breakdown
        "risk_scoring": {
            "final_score": case.final_risk_score,
            "decision": case.decision,
            "subscores": {
                "phase1_prior": subscores.get("phase1_prior", 0.0),
                "behavior": behavior_score,
                "graph": graph_score,
                "kyc": kyc_score,
            },
            "explanation": behavioral.get("risk_explanation", ""),
        },

        # SAR dossier
        "dossier": state.get("dossier", ""),
    }
