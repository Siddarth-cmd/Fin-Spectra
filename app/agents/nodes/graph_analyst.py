from ..state import InvestigationState
from ..tools import build_and_analyze_graph_tool

def graph_analyst_node(state: InvestigationState) -> InvestigationState:
    """
    Phase 8: Real Graph Analysis Agent
    Builds a NetworkX directed graph from database transactions (Nodes = accounts, Edges = transactions).
    Calculates degree, in-degree, out-degree, centrality, fan-in/out, cycles, 2-hop neighbors, and intermediary nodes.
    Attaches source transaction record citations.
    """
    entity_id = state.get("entity_id", "")

    # Invoke tool to perform graph computation via NetworkX
    graph_res = build_and_analyze_graph_tool(entity_id)

    graph_metrics = {
        "account_count": graph_res.get("nodes_count", 0),
        "beneficiary_count": graph_res.get("two_hop_neighbors_count", 0),
        "device_count": 1,
        "transaction_count": graph_res.get("edges_count", 0),
        "target_in_degree": graph_res.get("target_in_degree", 0),
        "target_out_degree": graph_res.get("target_out_degree", 0),
        "target_centrality": graph_res.get("target_centrality", 0.0),
        "cycles_detected": graph_res.get("cycles_detected", False),
        "cycles_count": graph_res.get("cycles_count", 0),
        "two_hop_neighbors": graph_res.get("two_hop_neighbors_count", 0),
        "fan_in_ratio": graph_res.get("fan_in_ratio", 0.0),
        "fan_out_ratio": graph_res.get("fan_out_ratio", 0.0),
        "multi_beneficiary_flag": 1 if graph_res.get("target_out_degree", 0) >= 2 else 0,
        "self_transfer_detected": graph_res.get("cycles_detected", False),
        "source_records": graph_res.get("source_records", []),

        # Backward compatibility aliases
        "counterparty_hubs": 1 if graph_res.get("target_out_degree", 0) >= 2 else 0,
        "shell_intermediaries_suspected": graph_res.get("cycles_detected", False),
        "circular_paths_detected": graph_res.get("cycles_detected", False)
    }

    state["graph_metrics"] = graph_metrics

    for t in state.get("task_list", []):
        if t["name"] == "ANALYZE_GRAPH":
            t["status"] = "COMPLETED"

    return state
