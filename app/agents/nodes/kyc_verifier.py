from ..state import InvestigationState

def kyc_verifier_node(state: InvestigationState) -> InvestigationState:
    """
    Verifies customer profile (occupation, risk level, account age, devices) against actual transaction behavior.
    Reads directly from real trigger_evidence customer context.
    """
    trigger_evidence = state.get("trigger_evidence", {})
    customer = trigger_evidence.get("customer") or {}
    behavioral = state.get("behavioral_metrics", {})
    
    # Real customer fields
    name = customer.get("name", "Unknown")
    occupation = customer.get("occupation", "N/A")
    risk_level = customer.get("risk_level", "LOW")
    account_age_days = customer.get("account_age_days", 0)
    
    total_volume_in = behavioral.get("total_volume_in", 0.0)
    total_volume_out = behavioral.get("total_volume_out", 0.0)
    total_volume = max(total_volume_in, total_volume_out)
    
    # Dynamic evaluation using real customer data
    verdicts = []
    
    if risk_level.upper() in ["HIGH", "CRITICAL"]:
        verdicts.append(f"High-Risk Customer Tier ({risk_level})")
        
    if account_age_days < 180 and total_volume > 10000:
        verdicts.append(f"New Account Surge (Age: {account_age_days} days, Vol: ${total_volume:,.2f})")
        
    if occupation in ["Student", "Unemployed"]:
        if total_volume > 5000:
            verdicts.append(f"ALERT: High turnover (${total_volume:,.2f}) inconsistent with declared occupation ({occupation})")
        else:
            verdicts.append(f"Turnover consistent with occupation ({occupation})")
    elif occupation in ["Manager", "Software Engineer", "Consultant", "Director", "Executive"]:
        if total_volume > 100000:
            verdicts.append(f"ALERT: Exceptionally high turnover (${total_volume:,.2f}) for professional occupation ({occupation})")
        else:
            verdicts.append(f"Turnover within expected limits for occupation ({occupation})")
    else:
        verdicts.append(f"Occupation evaluated: {occupation} | Risk Level: {risk_level}")
        
    verdict_text = " | ".join(verdicts)
    
    current_kyc = state.get("kyc_notes", "")
    state["kyc_notes"] = f"{current_kyc} || KYC Verification: {verdict_text}"
    
    for t in state.get("task_list", []):
        if t["name"] == "VERIFY_KYC":
            t["status"] = "COMPLETED"
            
    return state
