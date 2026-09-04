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
    
    # Final Output
    dossier: str
    final_risk_score: float
    decision: str # ALLOW, REVIEW, BLOCK

