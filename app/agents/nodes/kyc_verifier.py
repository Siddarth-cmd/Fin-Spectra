from ..state import InvestigationState

def kyc_verifier_node(state: InvestigationState) -> InvestigationState:
    """
    Matches declared KYC occupation vs actual volume & velocity turnover.
    """
    kyc_notes = state.get("kyc_notes", "")
    behavioral = state.get("behavioral_metrics", {})
    
    # Simple heuristic
    total_in = behavioral.get("total_volume_in", 0)
    
    if "Student" in kyc_notes or "Unemployed" in kyc_notes:
        if total_in > 10000:
            state["kyc_notes"] += " | ALERT: High volume inconsistent with declared occupation."
        else:
            state["kyc_notes"] += " | Volume consistent with occupation."
    elif "Software Engineer" in kyc_notes or "Consultant" in kyc_notes:
        if total_in > 50000:
            state["kyc_notes"] += " | ALERT: High volume inconsistent with declared occupation."
        else:
            state["kyc_notes"] += " | Volume consistent with occupation."
    elif "Restaurant Owner" in kyc_notes:
        # Expected high cash flow
        state["kyc_notes"] += " | Volume typical for commercial retail."
        
    for t in state.get("task_list", []):
        if t["name"] == "VERIFY_KYC":
            t["status"] = "COMPLETED"
            
    return state
