from ..state import InvestigationState
from ..llm_client import LLMClient
import json

def case_assembler_node(state: InvestigationState) -> InvestigationState:
    """
    Compiles the dossier narrative SAR and updates the final persisted state snapshot in Neon PostgreSQL DB.
    """
    state["loop_count"] = state.get("loop_count", 0) + 1
    
    is_complete = True
    if state["loop_count"] < 2 and not state.get("ledger_history"):
        is_complete = False
        state["missing_evidence"] = ["Missing full ledger history"]
        
    if is_complete:
        llm = LLMClient()
        system_prompt = (
            "You are drafting a Suspicious Activity Report (SAR) narrative dossier. "
            "Summarize the typology, rationale, decision, and risk findings in markdown format."
        )
        evidence = {
            "typology": state.get("typology_classification"),
            "rationale": state.get("typology_rationale"),
            "kyc": state.get("kyc_notes"),
            "graph": state.get("graph_metrics"),
            "final_risk_score": state.get("final_risk_score"),
            "decision": state.get("decision")
        }
        
        user_prompt = f"Evidence to compile:\n{json.dumps(evidence, indent=2)}"
        try:
            dossier = llm.generate(system_prompt, user_prompt)
            state["dossier"] = dossier
        except Exception as e:
            state["dossier"] = f"Failed to generate dossier: {str(e)}"
            
    # Persist the final state snapshot (including dossier) to Neon PostgreSQL
    try:
        from ...database import SessionLocal
        from ...models.schema import InvestigationCase
        db = SessionLocal()
        try:
            case = db.query(InvestigationCase).filter(InvestigationCase.id == state["case_id"]).first()
            if case:
                case.state_snapshot_json = dict(state)
                db.commit()
        finally:
            db.close()
    except Exception:
        pass

    return state
