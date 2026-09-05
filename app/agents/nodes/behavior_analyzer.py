from ..state import InvestigationState
from ..tools import calculate_behavior_metrics_tool

def behavior_analyzer_node(state: InvestigationState) -> InvestigationState:
    """
    Phase 6: Real Behavior Analysis Agent
    Calculates statistics from historical database transactions.
    Computes count, total inflow, total outflow, mean, stddev, velocity, surge, pass-through ratio, and Z-score.
    """
    ledger = state.get("ledger_history", [])
    trigger_ev = state.get("trigger_evidence") or {}
    trigger_tx = trigger_ev.get("transaction") or {}

    trigger_tx_id = str(trigger_tx.get("transaction_id", ""))
    trigger_amount = float(trigger_tx.get("amount", 0.0))

    if trigger_amount == 0.0 and ledger:
        trigger_amount = float(ledger[0].get("amount", 0.0))

    # Invoke tool to calculate exact statistical metrics
    stats = calculate_behavior_metrics_tool(ledger, trigger_tx_id, trigger_amount)

    total_in = sum(t["amount"] for t in ledger if t.get("dir") == "IN" or t.get("receiver_account_id"))
    total_out = sum(t["amount"] for t in ledger if t.get("dir") == "OUT" or t.get("beneficiary_id"))
    if total_in == 0.0 and ledger:
        total_in = sum(t["amount"] for t in ledger)

    behavioral_metrics = {
        "total_volume_in": round(total_in, 2),
        "total_volume_out": round(total_out, 2),
        "velocity_z_score": stats["velocity_z_score"],
        "pass_through_ratio": stats["pass_through_ratio"],
        "trigger_amount": trigger_amount,
        "historical_transaction_count": stats["historical_count"],
        "historical_mean": stats["historical_mean"],
        "historical_stddev": stats["historical_stddev"],
        "effective_stddev": stats.get("effective_stddev", 0.0),
        "velocity_baseline_status": stats["baseline_status"],
        "source_records": [t.get("transaction_id") or t.get("id") for t in ledger if t.get("id")]
    }

    state["behavioral_metrics"] = behavioral_metrics

    for t in state.get("task_list", []):
        if t["name"] == "ANALYZE_BEHAVIOR":
            t["status"] = "COMPLETED"

    return state
