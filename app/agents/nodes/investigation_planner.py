from ..state import InvestigationState
from ..llm_client import LLMClient
import json

def investigation_planner_node(state: InvestigationState) -> InvestigationState:
    """
    Dynamic planner generating the investigation steps based on the findings so far.
    """
    llm = LLMClient()
    
    system_prompt = """
    You are an AI Investigation Planner. Based on the typology and current evidence, outline a dynamic 3-to-5 step investigation plan.
    Provide your answer in strict JSON format:
    {
      "plan": [
        "Step 1...",
        "Step 2..."
      ]
    }
    """
    
    evidence = {
        "typology_classification": state.get("typology_classification"),
        "typology_rationale": state.get("typology_rationale"),
        "graph_metrics": state.get("graph_metrics")
    }
    
    user_prompt = f"Context:\n{json.dumps(evidence, indent=2)}"
    
    try:
        response = llm.generate(system_prompt, user_prompt)
        if "{" in response and "}" in response:
            json_str = response[response.find("{"):response.rfind("}")+1]
            result = json.loads(json_str)
            state["investigation_plan"] = result.get("plan", [])
        else:
            state["investigation_plan"] = ["Review counterparty flows.", "Verify KYC occupation.", "Ascertain source of funds."]
    except Exception:
        state["investigation_plan"] = ["Review counterparty flows.", "Verify KYC occupation.", "Ascertain source of funds."]
        
    return state
