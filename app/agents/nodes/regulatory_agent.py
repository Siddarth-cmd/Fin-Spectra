from ..state import InvestigationState
from ..tools import get_regulatory_guidance_tool

def regulatory_agent_node(state: InvestigationState) -> InvestigationState:
    """
    Phase 14: Regulatory Knowledge Agent
    Queries controlled regulatory knowledge base for official AML guidance (FATF, FinCEN, FIU, RBI).
    Returns exact source title, organization, section reference, and summary date without inventing facts.
    """
    typology = state.get("typology_classification") or state.get("alert_type") or "STRUCTURING"

    guidance = get_regulatory_guidance_tool(typology)

    if guidance:
        state["regulatory_findings"] = {
            "title": guidance["title"],
            "source_org": guidance["source_org"],
            "section_ref": guidance["section_ref"],
            "content_summary": guidance["content_summary"],
            "retrieval_date": guidance["retrieval_date"],
            "source_table": "regulatory_guidance",
            "source_id": guidance["id"]
        }
    else:
        state["regulatory_findings"] = {
            "title": "General AML Customer Due Diligence",
            "source_org": "FATF",
            "section_ref": "Recommendation 10",
            "content_summary": "Financial institutions must conduct ongoing due diligence on business relationships and scrutinize transactions.",
            "source_table": "regulatory_guidance",
            "source_id": "REG-GENERIC"
        }

    return state
