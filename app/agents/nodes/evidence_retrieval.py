from ..state import InvestigationState
from typing import Dict, Any, List

def evidence_retrieval_node(state: InvestigationState) -> InvestigationState:
    """
    Retrieves real evidence from trigger_evidence and Neon DB for the investigated entity.
    """
    trigger_evidence = state.get("trigger_evidence", {})
    entity_id = state.get("entity_id", "")

    customer = trigger_evidence.get("customer") or {}
    transaction = trigger_evidence.get("transaction") or {}
    tx_account = trigger_evidence.get("transaction_account") or {}
    tx_beneficiary = trigger_evidence.get("transaction_beneficiary") or {}
    accounts = trigger_evidence.get("accounts") or []
    beneficiaries = trigger_evidence.get("beneficiaries") or []
    devices = trigger_evidence.get("devices") or []

    # 1. Populate KYC notes from real customer & account context
    if customer:
        acc_type = tx_account.get("account_type") or (accounts[0].get("account_type") if accounts else "N/A")
        state["kyc_notes"] = (
            f"Customer: {customer.get('name', 'N/A')} (ID: {customer.get('customer_id')}) | "
            f"Occupation: {customer.get('occupation', 'N/A')} | "
            f"Risk Level: {customer.get('risk_level', 'N/A')} | "
            f"Account Age: {customer.get('account_age_days', 0)} days | "
            f"Primary Account Type: {acc_type} | "
            f"Registered Devices: {len(devices)} | "
            f"Beneficiaries Count: {len(beneficiaries)}"
        )
    else:
        state["kyc_notes"] = "MISSING_REAL_CUSTOMER_DATA"

    # 2. Populate Ledger History from real transactions (query Neon DB or fallback to trigger_evidence transaction)
    ledger = []
    try:
        from ...database import SessionLocal
        from ...models.schema import Transaction, InvestigationCase
        db = SessionLocal()
        try:
            # Query Neon DB transactions for entity_id (customer_id)
            txs = (
                db.query(Transaction)
                .filter(Transaction.customer_id == entity_id)
                .order_by(Transaction.transaction_timestamp.desc())
                .limit(50)
                .all()
            )
            for t in txs:
                ledger.append({
                    "id": t.transaction_id,
                    "dir": "OUT" if t.transaction_type in ["TRANSFER", "PAYMENT", "WITHDRAWAL"] else "IN",
                    "amount": float(t.amount) if t.amount is not None else 0.0,
                    "channel": t.transaction_type or "TRANSFER",
                    "time": t.transaction_timestamp.isoformat() if t.transaction_timestamp else ""
                })

            # Fetch Historical Cases from DB
            past_cases = (
                db.query(InvestigationCase)
                .filter(InvestigationCase.entity_id == entity_id, InvestigationCase.id != state["case_id"])
                .all()
            )
            state["historical_cases"] = [
                {"case_id": c.id, "decision": c.decision, "score": c.final_risk_score} for c in past_cases
            ]
        finally:
            db.close()
    except Exception:
        pass

    # If DB query returned no ledger rows, use the real primary transaction from trigger_evidence
    if not ledger and transaction:
        tx_type = transaction.get("transaction_type", "TRANSFER")
        ledger.append({
            "id": transaction.get("transaction_id", "TX_UNKNOWN"),
            "dir": "OUT" if tx_type in ["TRANSFER", "PAYMENT", "WITHDRAWAL"] else "IN",
            "amount": float(transaction.get("amount", 0.0)),
            "channel": tx_type,
            "time": transaction.get("transaction_timestamp", "")
        })

    state["ledger_history"] = sorted(ledger, key=lambda x: x.get("time", ""))

    # 3. Populate Balance History summary
    state["balance_history"] = {
        "primary_account_id": tx_account.get("account_id", "N/A"),
        "account_status": tx_account.get("status", "ACTIVE"),
        "total_accounts_count": len(accounts)
    }

    # Mark FETCH_EVIDENCE task as completed
    for t in state.get("task_list", []):
        if t["name"] == "FETCH_EVIDENCE":
            t["status"] = "COMPLETED"

    return state
