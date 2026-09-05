from typing import TypedDict, List, Dict, Any, Optional

class TaskItem(TypedDict):
    task_id: str
    name: str
    status: str # PENDING, IN_PROGRESS, COMPLETED, FAILED
    required_evidence_key: str

class InvestigationState(TypedDict):
    """
    The shared state (memory) for the Task-Driven LangGraph investigation pipeline.
    This state is persisted via checkpointer.
    """
    # Core Identifiers
    case_id: str
    alert_id: str
    entity_id: str
    
    # Alert Input
    alert_type: str
    raw_priority_score: float
    trigger_evidence: Dict[str, Any]
    
    # Task Queue & Plan Management
    task_list: List[Dict[str, Any]]
    current_task: str
    plan_satisfied: bool
    
    # Memory / History
    historical_cases: List[Dict[str, Any]]
    
    # Evidence Retrieval & Metrics
    ledger_history: List[Dict[str, Any]]
    balance_history: Dict[str, Any]
    behavioral_metrics: Dict[str, Any]
    graph_metrics: Dict[str, Any]
    kyc_notes: str
    
    # Typology & Plan
    typology_classification: str
    typology_rationale: str
    forensic_questions: List[Dict[str, str]]
    investigation_plan: List[str]
    
    # Loop tracking
    loop_count: int
    missing_evidence: List[str]
    evidence_found: bool
    
    # Extended Agent Metrics & Lineage
    kyc_metrics: Dict[str, Any]
    regulatory_findings: Dict[str, Any]
    detected_typology_evidence: Dict[str, Any]
    risk_factors_breakdown: List[Dict[str, Any]]
    explainable_findings: Dict[str, Any]
    evidence_provenance_lineage: List[Dict[str, Any]]

    # Final Output
    dossier: str
    final_risk_score: float
    decision: str # ALLOW, REVIEW, BLOCK

def create_initial_state_from_neon_alert(enriched_alert: Dict[str, Any]) -> InvestigationState:
    """
    Adapter function mapping enriched Neon alert repository dictionary into an initial InvestigationState.
    """
    alert_data = enriched_alert.get("alert", {})
    alert_id = str(alert_data.get("alert_id", "UNKNOWN"))
    customer_id = str(alert_data.get("customer_id", "UNKNOWN"))
    alert_type = str(alert_data.get("alert_type", "UNKNOWN"))
    risk_score = float(alert_data.get("risk_score", 0.0))

    case_id = f"CASE_{alert_id}"

    return {
        "case_id": case_id,
        "alert_id": alert_id,
        "entity_id": customer_id,
        "alert_type": alert_type,
        "raw_priority_score": risk_score,
        "trigger_evidence": enriched_alert,
        "task_list": [],
        "current_task": "",
        "plan_satisfied": False,
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
        "loop_count": 0,
        "missing_evidence": [],
        "evidence_found": True,
        "dossier": "",
        "final_risk_score": 0.0,
        "decision": ""
    }
