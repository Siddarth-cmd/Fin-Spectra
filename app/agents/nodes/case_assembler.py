import json
from ..state import InvestigationState
from ..llm_client import LLMClient

SYSTEM_PROMPT = (
    "You are an expert AML forensic compliance investigator drafting a Suspicious Activity Report (SAR) narrative dossier.\n"
    "STRICT GROUNDING INSTRUCTIONS:\n"
    "1. Use ONLY facts present in the supplied InvestigationState evidence.\n"
    "2. Do NOT invent dates, locations, transaction purposes, counterparties, customer behavior, or compliance conclusions.\n"
    "3. Do NOT infer facts that are not explicitly supported by the evidence.\n"
    "4. If specific evidence is missing or unprovided, explicitly state: 'Not available in investigation evidence.'\n"
    "5. Clearly distinguish observed factual evidence from analytical interpretation.\n"
    "Summarize the evidence, typology classification, risk scores, and decision in clear markdown format."
)

def case_assembler_node(state: InvestigationState) -> InvestigationState:
    """
    Compiles the dossier narrative SAR grounded strictly in compact InvestigationState evidence
    and updates the final persisted state snapshot in Neon PostgreSQL DB.
    """
    state["loop_count"] = state.get("loop_count", 0) + 1
    
    is_complete = True
    if state["loop_count"] < 2 and not state.get("ledger_history"):
        is_complete = False
        state["missing_evidence"] = ["Missing full ledger history"]
        
    if is_complete:
        llm = LLMClient()
        
        trigger_ev = state.get("trigger_evidence") or {}
        customer = trigger_ev.get("customer") or {}

        evidence = {
            "alert_id": state.get("alert_id"),
            "alert_type": state.get("alert_type"),
            "typology_classification": state.get("typology_classification"),
            "typology_rationale": state.get("typology_rationale"),
            "behavioral_metrics": state.get("behavioral_metrics"),
            "graph_metrics": state.get("graph_metrics"),
            "kyc_summary": {
                "occupation": customer.get("occupation", "Not available"),
                "risk_level": customer.get("risk_level", "Not available"),
                "account_age_days": customer.get("account_age_days", "Not available")
            },
            "final_risk_score": state.get("final_risk_score"),
            "decision": state.get("decision")
        }
        
        user_prompt = f"Investigation Evidence Payload:\n{json.dumps(evidence, indent=2, default=str)}"
        try:
            dossier = llm.generate(SYSTEM_PROMPT, user_prompt)
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
