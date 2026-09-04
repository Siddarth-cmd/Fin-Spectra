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
