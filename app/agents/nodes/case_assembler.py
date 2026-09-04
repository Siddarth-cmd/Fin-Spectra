from ..state import InvestigationState
from ..llm_client import LLMClient
import json

def case_assembler_node(state: InvestigationState) -> InvestigationState:
    """
    Compiles the dossier and checks for completeness. Loop-back routing is handled 
    by conditional edges in the orchestrator, but we prep the logic here.
    """
    state["loop_count"] = state.get("loop_count", 0) + 1
    
    # Mock completeness check (in real app, we'd verify if all forensic questions have answers)
    is_complete = True
    if state["loop_count"] < 2 and not state.get("ledger_history"):
        is_complete = False
        state["missing_evidence"] = ["Missing full ledger history"]
        
    if is_complete:
        llm = LLMClient()
        system_prompt = "You are drafting a Suspicious Activity Report (SAR) narrative dossier. Summarize the typology, rationale, and findings in markdown format."
        evidence = {
            "typology": state.get("typology_classification"),
            "rationale": state.get("typology_rationale"),
            "kyc": state.get("kyc_notes"),
            "graph": state.get("graph_metrics")
        }
        
        user_prompt = f"Evidence to compile:\n{json.dumps(evidence, indent=2)}"
        try:
            dossier = llm.generate(system_prompt, user_prompt)
            state["dossier"] = dossier
        except Exception as e:
            state["dossier"] = f"Failed to generate dossier: {str(e)}"
            
    return state
