from ..state import InvestigationState

def plan_checker_node(state: InvestigationState) -> InvestigationState:
    """
    Plan Satisfaction Checker: Verifies if all tasks in task_list are COMPLETED 
    and that required evidence fields in InvestigationState are satisfied.
    """
    task_list = state.get("task_list", [])
    missing = []
    
    # Check completeness of evidence for required task items
    for task in task_list:
        req_key = task.get("required_evidence_key")
        if req_key and not state.get(req_key):
            missing.append(f"Missing evidence for task {task['name']} ({req_key})")
            
    state["missing_evidence"] = missing
    
    # Plan is satisfied if no tasks are PENDING and no missing required evidence
    all_tasks_completed = all(t.get("status") == "COMPLETED" for t in task_list)
    
    if all_tasks_completed and not missing:
        state["plan_satisfied"] = True
    else:
        state["plan_satisfied"] = False
        state["loop_count"] = state.get("loop_count", 0) + 1
        
    return state
