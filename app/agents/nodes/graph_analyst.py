from ..state import InvestigationState

def graph_analyst_node(state: InvestigationState) -> InvestigationState:
    """
    Analyzes customer entity relationship topology (Accounts, Beneficiaries, Devices, Ledger)
    derived directly from trigger_evidence and ledger_history.
    
    Metrics:
    - account_count: Number of customer accounts
    - beneficiary_count: Number of registered beneficiaries
    - device_count: Number of registered devices
    - transaction_count: Total transactions in ledger history
    - unique_beneficiaries: Distinct beneficiary IDs referenced
    - tx_per_account: Average transaction volume per account (formerly fan_in_ratio)
    - beneficiary_dispersion_ratio: Unique beneficiaries per transaction (formerly fan_out_ratio)
    - multi_beneficiary_flag: 1 if customer has >= 2 beneficiaries, else 0 (formerly counterparty_hubs)
    - multi_device_multi_beneficiary_flag: True if multi-device & multi-beneficiary present (formerly shell_intermediaries_suspected)
    - self_transfer_detected: True if account-to-self transfer detected (formerly circular_paths_detected)
    """
    trigger_evidence = state.get("trigger_evidence", {})
    ledger = state.get("ledger_history", [])

    customer = trigger_evidence.get("customer") or {}
    accounts = trigger_evidence.get("accounts") or []
    beneficiaries = trigger_evidence.get("beneficiaries") or []
    devices = trigger_evidence.get("devices") or []
    tx = trigger_evidence.get("transaction") or {}

    account_count = len(accounts)
    beneficiary_count = len(beneficiaries)
    device_count = len(devices)
    tx_count = len(ledger)

    # 1. Unique Beneficiaries & Dispersion
    beneficiary_ids = {b.get("beneficiary_id") for b in beneficiaries if b.get("beneficiary_id")}
    if tx.get("beneficiary_id"):
        beneficiary_ids.add(tx.get("beneficiary_id"))
    
    unique_beneficiaries_count = len(beneficiary_ids)

    # 2. Transaction Density & Beneficiary Dispersion Ratios
    beneficiary_dispersion_ratio = (unique_beneficiaries_count / tx_count) if tx_count > 0 else 0.0
    tx_per_account = (tx_count / account_count) if account_count > 0 else 0.0

    # 3. Multi-Beneficiary Flag
    multi_beneficiary_flag = 1 if beneficiary_count >= 2 else 0

    # 4. Multi-Device & Multi-Beneficiary Flag
    multi_device_multi_beneficiary_flag = bool(device_count >= 2 and beneficiary_count >= 2)

    # 5. Self-Transfer Detection
    customer_acc_ids = {acc.get("account_id") for acc in accounts if acc.get("account_id")}
    self_transfer_detected = False
    for item in ledger:
        if item.get("id") in customer_acc_ids or (tx.get("account_id") and tx.get("account_id") == tx.get("beneficiary_id")):
            self_transfer_detected = True
            break

    # Compile graph metrics with renamed, accurate semantic labels
    graph_metrics = {
        "account_count": account_count,
        "beneficiary_count": beneficiary_count,
        "device_count": device_count,
        "transaction_count": tx_count,
        "unique_beneficiaries": unique_beneficiaries_count,
        "tx_per_account": round(tx_per_account, 2),
        "beneficiary_dispersion_ratio": round(beneficiary_dispersion_ratio, 2),
        "multi_beneficiary_flag": multi_beneficiary_flag,
        "multi_device_multi_beneficiary_flag": multi_device_multi_beneficiary_flag,
        "self_transfer_detected": self_transfer_detected,

        # Backward compatibility aliases for existing scoring rules
        "counterparty_hubs": multi_beneficiary_flag,
        "shell_intermediaries_suspected": multi_device_multi_beneficiary_flag,
        "circular_paths_detected": self_transfer_detected,
        "fan_in_ratio": round(tx_per_account, 2),
        "fan_out_ratio": round(beneficiary_dispersion_ratio, 2)
    }

    state["graph_metrics"] = graph_metrics

    # Mark ANALYZE_GRAPH task as completed
    for t in state.get("task_list", []):
        if t["name"] == "ANALYZE_GRAPH":
            t["status"] = "COMPLETED"

    return state
