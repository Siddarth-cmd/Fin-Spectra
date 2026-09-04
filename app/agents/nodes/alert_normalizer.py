from ..state import InvestigationState

def alert_normalizer_node(state: InvestigationState) -> InvestigationState:
    """
    Initializes the state. In a real system, it might fetch the ClassifiedAlert 
    from a queue. Here we assume the state was seeded with initial values.
    """
    # Initialize empty defaults if missing
    if "historical_cases" not in state: state["historical_cases"] = []
    if "ledger_history" not in state: state["ledger_history"] = []
    if "balance_history" not in state: state["balance_history"] = {}
    if "behavioral_metrics" not in state: state["behavioral_metrics"] = {}
    if "graph_metrics" not in state: state["graph_metrics"] = {}
    if "kyc_notes" not in state: state["kyc_notes"] = ""
    if "typology_classification" not in state: state["typology_classification"] = ""
    if "typology_rationale" not in state: state["typology_rationale"] = ""
    if "forensic_questions" not in state: state["forensic_questions"] = []
    if "investigation_plan" not in state: state["investigation_plan"] = []
    if "loop_count" not in state: state["loop_count"] = 0
    if "missing_evidence" not in state: state["missing_evidence"] = []
    if "dossier" not in state: state["dossier"] = ""
    if "final_risk_score" not in state: state["final_risk_score"] = 0.0
    if "decision" not in state: state["decision"] = ""
    
    return state
