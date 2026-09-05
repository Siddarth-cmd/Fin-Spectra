import json
from ..state import InvestigationState
from ..llm_client import LLMClient

ALLOWED_TYPOLOGIES = {
    "STRUCTURING",
    "LAYERING",
    "MULE_ACCOUNT",
    "FAN_IN",
    "FAN_OUT",
    "UNKNOWN"
}

def typology_classifier_node(state: InvestigationState) -> InvestigationState:
    """
    Uses the LLM to confirm the AML typology based on a compact evidence summary.
    Strictly validates output against ALLOWED_TYPOLOGIES.
    Falls back to 'UNKNOWN' on any failure or invalid output.
    """
    llm = LLMClient()
    
    system_prompt = """
    You are an expert AML compliance agent. Review the following evidence and determine the most likely money laundering typology.
    Provide your answer in strict JSON format:
    {
      "typology": "STRUCTURING|LAYERING|MULE_ACCOUNT|FAN_IN|FAN_OUT|UNKNOWN",
      "rationale": "Detailed explanation of why this typology fits the evidence."
    }
    """
    
    trigger_ev = state.get("trigger_evidence") or {}
    trigger_tx = trigger_ev.get("transaction") or {}
    customer = trigger_ev.get("customer") or {}
    behavior = state.get("behavioral_metrics") or {}
    graph = state.get("graph_metrics") or {}

    evidence_summary = {
        "alert_type": state.get("alert_type"),
        "trigger_transaction": {
            "amount": trigger_tx.get("amount", "Not available"),
            "transaction_type": trigger_tx.get("transaction_type", trigger_tx.get("type", "Not available"))
        },
        "behavioral_metrics": {
            "velocity_z_score": behavior.get("velocity_z_score", 0.0),
            "pass_through_ratio": behavior.get("pass_through_ratio", 0.0)
        },
        "graph_metrics": {
            "multi_beneficiary_flag": graph.get("multi_beneficiary_flag", 0),
            "multi_device_multi_beneficiary_flag": graph.get("multi_device_multi_beneficiary_flag", False),
            "self_transfer_detected": graph.get("self_transfer_detected", False),
            "beneficiary_dispersion_ratio": graph.get("beneficiary_dispersion_ratio", 0.0)
        },
        "kyc": {
            "occupation": customer.get("occupation", "Not available"),
            "risk_level": customer.get("risk_level", "Not available"),
            "account_age_days": customer.get("account_age_days", "Not available")
        }
    }
    
    user_prompt = f"Evidence Summary:\n{json.dumps(evidence_summary, indent=2, default=str)}"
    
    try:
        response = llm.generate(system_prompt, user_prompt)
        
        # 1. Check for JSON structure
        if "{" not in response or "}" not in response:
            state["typology_classification"] = "UNKNOWN"
            state["typology_rationale"] = f"Validation Error: LLM response did not contain JSON object. Response snippet: {response[:150]}"
            return state

        json_str = response[response.find("{"):response.rfind("}")+1]
        
        # 2. Parse JSON
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError as err:
            state["typology_classification"] = "UNKNOWN"
            state["typology_rationale"] = f"Validation Error: Malformed JSON returned by LLM ({str(err)})."
            return state

        # 3. Check for dictionary type
        if not isinstance(result, dict):
            state["typology_classification"] = "UNKNOWN"
            state["typology_rationale"] = "Validation Error: JSON response is not a valid JSON dictionary."
            return state

        # 4. Check for missing typology key
        if "typology" not in result or not result["typology"]:
            state["typology_classification"] = "UNKNOWN"
            state["typology_rationale"] = "Validation Error: Response missing required 'typology' field."
            return state

        raw_typology = str(result["typology"]).strip().upper()
        rationale = str(result.get("rationale", "")).strip()

        # 5. Validate against allowed set
        if raw_typology not in ALLOWED_TYPOLOGIES:
            state["typology_classification"] = "UNKNOWN"
            state["typology_rationale"] = f"Validation Error: Invalid typology '{raw_typology}' returned. Must be one of {sorted(list(ALLOWED_TYPOLOGIES))}."
            return state

        # Valid typology
        state["typology_classification"] = raw_typology
        state["typology_rationale"] = rationale if rationale else "Typology verified by LLM."

    except Exception as e:
        state["typology_classification"] = "UNKNOWN"
        state["typology_rationale"] = f"Failed to classify typology via LLM: {str(e)}"
        
    return state
