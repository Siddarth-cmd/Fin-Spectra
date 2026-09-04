from ..state import InvestigationState

def graph_analyst_node(state: InvestigationState) -> InvestigationState:
    """
    Analyzes 2-hop topological network for hubs, circular flows, and intermediaries.
    In a real app, this would use NetworkX on queried database records.
    """
    alert_type = state.get("alert_type", "")
    
    # Mocking graph analysis results based on the alert type
    graph_metrics = {
        "counterparty_hubs": 0,
        "circular_paths_detected": False,
        "shell_intermediaries_suspected": False,
        "fan_in_ratio": 0.0,
        "fan_out_ratio": 0.0
    }
    
    if alert_type == "FAN_IN_AGGREGATION":
        graph_metrics["fan_in_ratio"] = 12.5 # 12 senders to 1 receiver
        graph_metrics["counterparty_hubs"] = 1
    elif alert_type == "STRUCTURING":
        graph_metrics["fan_in_ratio"] = 4.0
    elif alert_type == "RAPID_MOVEMENT":
        graph_metrics["shell_intermediaries_suspected"] = True
        
    state["graph_metrics"] = graph_metrics
    
    for t in state.get("task_list", []):
        if t["name"] == "ANALYZE_GRAPH":
            t["status"] = "COMPLETED"
            
    return state
