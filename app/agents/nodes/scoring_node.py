from ..state import InvestigationState
from ...database import SessionLocal
from ...models.schema import InvestigationCase

def scoring_node(state: InvestigationState) -> InvestigationState:
    """
    Deterministic scoring and decision policy based on all accumulated evidence.
    """
    raw_score = state.get("raw_priority_score", 0.0)
    
    # Base score is the Phase 1 ranker score
    final_score = raw_score
    
    # Adjust based on Behavioral Metrics
    behavior = state.get("behavioral_metrics", {})
    z_score = behavior.get("velocity_z_score", 0.0)
    if z_score > 3.0:
        final_score += 15.0
    elif z_score > 1.5:
        final_score += 5.0
        
    # Adjust based on Graph Metrics
    graph = state.get("graph_metrics", {})
    if graph.get("circular_paths_detected"):
        final_score += 25.0
    if graph.get("shell_intermediaries_suspected"):
        final_score += 20.0
    if graph.get("counterparty_hubs", 0) > 0:
        final_score += 10.0
        
    # Adjust based on KYC
    kyc_notes = state.get("kyc_notes", "")
    if "ALERT" in kyc_notes:
        final_score += 15.0
        
    # Cap at 100
    final_score = min(final_score, 100.0)
    state["final_risk_score"] = final_score
    
    # Decision Thresholds
    if final_score <= 30:
        state["decision"] = "ALLOW"
    elif final_score <= 80:
        state["decision"] = "REVIEW"
    else:
        state["decision"] = "BLOCK"
        
    # Persist the final state to database memory
    db = SessionLocal()
    try:
        case = db.query(InvestigationCase).filter(InvestigationCase.id == state["case_id"]).first()
        if case:
            case.final_risk_score = final_score
            case.decision = state["decision"]
            case.state_snapshot_json = dict(state)
            db.commit()
    finally:
        db.close()
        
    return state
