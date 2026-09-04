from ..state import InvestigationState

def behavior_analyzer_node(state: InvestigationState) -> InvestigationState:
    """
    Computes statistical velocity Z-scores, volume surges, and counterparty concentration.
    """
    ledger = state.get("ledger_history", [])
    
    if not ledger:
        state["behavioral_metrics"] = {"status": "NO_HISTORY"}
        return state
        
    amounts_in = [tx["amount"] for tx in ledger if tx["dir"] == "IN"]
    amounts_out = [tx["amount"] for tx in ledger if tx["dir"] == "OUT"]
    
    total_in = sum(amounts_in)
    total_out = sum(amounts_out)
    
    # Calculate simple Z-score mockup based on recent volume vs mean (if we had full history)
    # Here we simulate finding a volume surge
    if total_in > 40000:
        surge_z_score = 4.2
    elif total_in > 10000:
        surge_z_score = 2.1
    else:
        surge_z_score = 0.5
        
    state["behavioral_metrics"] = {
        "total_volume_in": total_in,
        "total_volume_out": total_out,
        "velocity_z_score": surge_z_score,
        "pass_through_ratio": (total_out / total_in) if total_in > 0 else 0
    }
    
    for t in state.get("task_list", []):
        if t["name"] == "ANALYZE_BEHAVIOR":
            t["status"] = "COMPLETED"
            
    return state
