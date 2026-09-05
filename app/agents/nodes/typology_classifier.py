import json
from ..state import InvestigationState
from ..tools import detect_typologies_tool
from ..llm_client import LLMClient

ALLOWED_TYPOLOGIES = {
    "STRUCTURING",
    "RAPID_PASS_THROUGH",
    "FAN_IN",
    "FAN_OUT",
    "CIRCULAR_FLOW",
    "MULE_ACCOUNT",
    "UNKNOWN"
}

def typology_classifier_node(state: InvestigationState) -> InvestigationState:
    """
    Phase 7: Real Transaction Typology Detection Agent
    Runs deterministic detection logic for Structuring, Fan-In, Fan-Out, Rapid Pass-Through, Circular Flow
    operating on database transactions, validated by LLM reasoning.
    """
    ledger = state.get("ledger_history", [])
    entity_id = state.get("entity_id", "")

    # 1. Deterministic Detection Tool
    det_results = detect_typologies_tool(ledger, entity_id)

    primary_typology = det_results["primary_typology"]
    all_typologies = det_results["all_detected_typologies"]
    evidence_details = det_results["evidence_details"]

    # 2. LLM Verification
    llm = LLMClient()
    system_prompt = """
    You are an expert AML compliance investigator. Review the deterministic typology detection results
    derived from actual database transactions and confirm the primary classification.
    Return strict JSON:
    {
      "typology": "STRUCTURING|RAPID_PASS_THROUGH|FAN_IN|FAN_OUT|CIRCULAR_FLOW|MULE_ACCOUNT|UNKNOWN",
      "rationale": "Detailed evidence-grounded explanation."
    }
    """

    user_payload = {
        "entity_id": entity_id,
        "alert_type": state.get("alert_type"),
        "deterministic_primary": primary_typology,
        "all_detected": all_typologies,
        "evidence_details": evidence_details,
        "transaction_count": len(ledger)
    }

    try:
        response = llm.generate(system_prompt, f"Typology Evidence Payload:\n{json.dumps(user_payload, indent=2, default=str)}")
        if "{" in response and "}" in response:
            json_str = response[response.find("{"):response.rfind("}")+1]
            res = json.loads(json_str)
            raw_typ = str(res.get("typology", "")).upper()
            rationale = res.get("rationale", "")
            if raw_typ in ALLOWED_TYPOLOGIES:
                state["typology_classification"] = raw_typ
                state["typology_rationale"] = rationale
            else:
                state["typology_classification"] = primary_typology
                state["typology_rationale"] = f"Deterministic detection identified: {primary_typology}. LLM suggested {raw_typ}."
        else:
            state["typology_classification"] = primary_typology
            state["typology_rationale"] = f"Deterministic detection identified: {primary_typology}."
    except Exception as e:
        state["typology_classification"] = primary_typology
        state["typology_rationale"] = f"Deterministic detection identified: {primary_typology} (LLM verification bypassed: {str(e)})."

    state["detected_typology_evidence"] = evidence_details
    return state
