from ..state import InvestigationState

def kyc_verifier_node(state: InvestigationState) -> InvestigationState:
    """
    Phase 5: Real KYC Investigation Agent
    Performs quantitative analysis comparing declared income vs observed transaction volume (income_activity_ratio).
    Evaluates occupation consistency, account age surge, and risk profile with supporting record citations.
    """
    trigger_evidence = state.get("trigger_evidence", {})
    customer = trigger_evidence.get("customer") or {}
    behavioral = state.get("behavioral_metrics", {})
    ledger = state.get("ledger_history", [])

    # Real customer fields from DB
    customer_id = customer.get("customer_id", "UNKNOWN")
    name = customer.get("name", "Unknown")
    occupation = customer.get("occupation", "N/A")
    risk_level = customer.get("risk_level", "LOW")
    account_age_days = customer.get("account_age_days", 0)
    declared_income = float(customer.get("declared_income", 500000.0))

    # Observed annual / total volume from DB transactions
    total_volume_in = float(behavioral.get("total_volume_in", 0.0))
    total_volume_out = float(behavioral.get("total_volume_out", 0.0))
    observed_volume = max(total_volume_in, total_volume_out, sum(t.get("amount", 0.0) for t in ledger))

    # Calculate deterministic income activity ratio
    income_activity_ratio = round((observed_volume / declared_income), 2) if declared_income > 0 else 0.0

    verdicts = []
    source_records = [customer_id]

    if risk_level.upper() in ["HIGH", "CRITICAL"]:
        verdicts.append(f"High-Risk Customer Profile Tier ({risk_level})")

    if account_age_days < 180 and observed_volume > 500000.0:
        verdicts.append(f"New Account Surge (Age: {account_age_days} days, Observed Vol: ₹{observed_volume:,.2f})")

    # Income vs Turnover Analysis
    if income_activity_ratio > 3.0:
        verdicts.append(
            f"ALERT: Income Activity Ratio is {income_activity_ratio}x (Declared Income: ₹{declared_income:,.2f} vs Observed Volume: ₹{observed_volume:,.2f})"
        )
    else:
        verdicts.append(f"Income Activity Ratio ({income_activity_ratio}x) within expected limits for declared income (₹{declared_income:,.2f})")

    # Occupation Consistency Analysis
    if occupation in ["Student", "Unemployed"] and observed_volume > 100000.0:
        verdicts.append(f"ALERT: Turnover of ₹{observed_volume:,.2f} inconsistent with declared occupation ({occupation})")
    elif occupation in ["Manager", "Software Engineer", "Consultant", "Director", "Executive"]:
        if observed_volume > 10000000.0: # ₹1 Crore threshold
            verdicts.append(f"ALERT: Exceptionally high turnover (₹{observed_volume:,.2f}) for professional occupation ({occupation})")

    verdict_text = " | ".join(verdicts)

    state["kyc_metrics"] = {
        "customer_id": customer_id,
        "declared_income": declared_income,
        "observed_volume": observed_volume,
        "income_activity_ratio": income_activity_ratio,
        "occupation": occupation,
        "risk_level": risk_level,
        "account_age_days": account_age_days,
        "source_records": source_records,
        "verdict_summary": verdict_text
    }

    current_kyc = state.get("kyc_notes", "")
    state["kyc_notes"] = f"{current_kyc} || KYC Quantitative Verdict: {verdict_text} [Source Records: {customer_id}]"

    for t in state.get("task_list", []):
        if t["name"] == "VERIFY_KYC":
            t["status"] = "COMPLETED"

    return state
