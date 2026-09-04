import math
from ..state import InvestigationState

def behavior_analyzer_node(state: InvestigationState) -> InvestigationState:
    """
    Calculates statistical velocity Z-scores, volume surges, and pass-through ratios
    derived from real historical ledger transactions in Neon DB, using a calibrated variance floor.
    """
    ledger = state.get("ledger_history", [])
    trigger_evidence = state.get("trigger_evidence", {})
    trigger_tx = trigger_evidence.get("transaction") or {}

    # 1. Identify Trigger Transaction & Amount
    trigger_tx_id = str(trigger_tx.get("transaction_id", ""))
    trigger_amount = float(trigger_tx.get("amount", 0.0))

    # 2. Volumes & Pass-Through Ratio (All Ledger Transactions)
    amounts_in = [float(tx["amount"]) for tx in ledger if tx.get("dir") == "IN"]
    amounts_out = [float(tx["amount"]) for tx in ledger if tx.get("dir") == "OUT"]

    total_in = sum(amounts_in)
    total_out = sum(amounts_out)
    pass_through_ratio = round((total_out / total_in), 2) if total_in > 0 else 0.0

    # 3. Build Historical Baseline (Excluding Trigger Transaction)
    historical_txs = [
        tx for tx in ledger
        if str(tx.get("id")) != trigger_tx_id
    ]
    historical_amounts = [float(tx["amount"]) for tx in historical_txs]
    hist_count = len(historical_amounts)

    # 4. Calibrated Statistical Z-Score Calculation
    if hist_count < 3:
        hist_mean = round(sum(historical_amounts) / hist_count, 2) if hist_count > 0 else 0.0
        hist_stddev = 0.0
        effective_stddev = 0.0
        velocity_z_score = 0.0
        baseline_status = "INSUFFICIENT_HISTORICAL_SAMPLES"
    else:
        hist_mean = sum(historical_amounts) / hist_count
        variance = sum((x - hist_mean) ** 2 for x in historical_amounts) / hist_count
        hist_stddev = math.sqrt(variance)

        # Apply effective variance floor (20% of mean or actual stddev)
        effective_stddev = max(hist_stddev, 0.20 * hist_mean)

        if effective_stddev == 0:
            velocity_z_score = 0.0
            baseline_status = "ZERO_VARIANCE"
        else:
            z_raw = (trigger_amount - hist_mean) / effective_stddev
            velocity_z_score = min(round(z_raw, 2), 5.0)
            baseline_status = "COMPUTED"

        hist_mean = round(hist_mean, 2)
        hist_stddev = round(hist_stddev, 2)
        effective_stddev = round(effective_stddev, 2)

    # Compile behavioral metrics dict
    existing_behavioral = state.get("behavioral_metrics") or {}
    behavioral_metrics = {
        "total_volume_in": total_in,
        "total_volume_out": total_out,
        "velocity_z_score": velocity_z_score,
        "pass_through_ratio": pass_through_ratio,
        "trigger_amount": trigger_amount,
        "historical_transaction_count": hist_count,
        "historical_mean": hist_mean,
        "historical_stddev": hist_stddev,
        "effective_stddev": effective_stddev,
        "velocity_baseline_status": baseline_status
    }

    # Preserve any subscores/explanations if already populated downstream
    for k, v in existing_behavioral.items():
        if k not in behavioral_metrics:
            behavioral_metrics[k] = v

    state["behavioral_metrics"] = behavioral_metrics

    # Mark ANALYZE_BEHAVIOR task as completed
    for t in state.get("task_list", []):
        if t["name"] == "ANALYZE_BEHAVIOR":
            t["status"] = "COMPLETED"

    return state
