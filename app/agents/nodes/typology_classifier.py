from ..state import InvestigationState
from ..llm_client import LLMClient
import json

def typology_classifier_node(state: InvestigationState) -> InvestigationState:
    """
    Uses the Groq LLM to confirm the AML typology based on the facts gathered so far.
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
    
    evidence = {
        "alert_type": state.get("alert_type"),
        "trigger_evidence": state.get("trigger_evidence"),
        "behavioral_metrics": state.get("behavioral_metrics"),
        "graph_metrics": state.get("graph_metrics"),
        "kyc_notes": state.get("kyc_notes")
    }
    
    user_prompt = f"Evidence:\n{json.dumps(evidence, indent=2)}"
    
    try:
        response = llm.generate(system_prompt, user_prompt)
        # Attempt to parse JSON from response
        # In a robust system, we would use structured output / function calling
        if "{" in response and "}" in response:
            json_str = response[response.find("{"):response.rfind("}")+1]
            result = json.loads(json_str)
            state["typology_classification"] = result.get("typology", "UNKNOWN")
            state["typology_rationale"] = result.get("rationale", "")
        else:
            state["typology_classification"] = state.get("alert_type") # Fallback to original alert
            state["typology_rationale"] = response
    except Exception as e:
        state["typology_classification"] = state.get("alert_type")
        state["typology_rationale"] = f"Failed to classify typology via LLM: {str(e)}"
        
    return state
