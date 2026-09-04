from ..state import InvestigationState
from typing import List, Dict, Any

def task_planner_node(state: InvestigationState) -> InvestigationState:
    """
    Studies the incoming alert JSON request and builds a Task List based on 
    the static investigation plan template for the alert type.
    """
    alert_type = state.get("alert_type", "").upper()
    
    # Base Task Templates based on Alert Type
    if "STRUCTURING" in alert_type:
        tasks = [
            {"task_id": "T1", "name": "FETCH_EVIDENCE", "status": "PENDING", "required_evidence_key": "ledger_history"},
            {"task_id": "T2", "name": "VERIFY_KYC", "status": "PENDING", "required_evidence_key": "kyc_notes"},
            {"task_id": "T3", "name": "ANALYZE_BEHAVIOR", "status": "PENDING", "required_evidence_key": "behavioral_metrics"}
        ]
        plan_desc = ["Fetch transaction history", "Verify KYC & occupation", "Analyze velocity Z-scores for structuring thresholds"]
    elif "FAN_IN" in alert_type or "FAN_OUT" in alert_type or "RAPID" in alert_type:
        tasks = [
            {"task_id": "T1", "name": "FETCH_EVIDENCE", "status": "PENDING", "required_evidence_key": "ledger_history"},
            {"task_id": "T2", "name": "ANALYZE_GRAPH", "status": "PENDING", "required_evidence_key": "graph_metrics"},
            {"task_id": "T3", "name": "ANALYZE_BEHAVIOR", "status": "PENDING", "required_evidence_key": "behavioral_metrics"},
            {"task_id": "T4", "name": "VERIFY_KYC", "status": "PENDING", "required_evidence_key": "kyc_notes"}
        ]
        plan_desc = ["Fetch transaction ledger", "Analyze network topology for hubs & pass-through", "Compute velocity metrics", "Verify customer profile"]
    else:
        # Default comprehensive plan template
        tasks = [
            {"task_id": "T1", "name": "FETCH_EVIDENCE", "status": "PENDING", "required_evidence_key": "ledger_history"},
            {"task_id": "T2", "name": "VERIFY_KYC", "status": "PENDING", "required_evidence_key": "kyc_notes"},
            {"task_id": "T3", "name": "ANALYZE_BEHAVIOR", "status": "PENDING", "required_evidence_key": "behavioral_metrics"},
            {"task_id": "T4", "name": "ANALYZE_GRAPH", "status": "PENDING", "required_evidence_key": "graph_metrics"}
        ]
        plan_desc = ["Retrieve ledger and past cases", "Perform KYC verification", "Compute behavioral metrics", "Analyze 2-hop transaction network graph"]

    state["task_list"] = tasks
    state["investigation_plan"] = plan_desc
    state["plan_satisfied"] = False
    state["loop_count"] = 0
    state["missing_evidence"] = []
    
    return state
