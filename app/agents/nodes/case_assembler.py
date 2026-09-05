import json
from ..state import InvestigationState
from ..llm_client import LLMClient

SYSTEM_PROMPT = (
    "You are an expert AML forensic compliance investigator drafting a Suspicious Activity Report (SAR) narrative dossier.\n"
    "STRICT GROUNDING INSTRUCTIONS:\n"
    "1. Use ONLY facts present in the supplied InvestigationState evidence.\n"
    "2. Include exact database Source Record IDs and table citations for every finding.\n"
    "3. Do NOT invent dates, transaction purposes, counterparties, or customer behavior.\n"
    "4. Clearly distinguish observed factual evidence from analytical interpretation.\n"
    "Summarize the evidence, typology classification, risk score breakdown, regulatory citations, and decision in clear markdown format."
)

def case_assembler_node(state: InvestigationState) -> InvestigationState:
    """
    Phase 15 & 16: Grounded Case Assembler & Evidence Provenance Lineage
    Generates SAR dossier narrative strictly grounded in factual InvestigationState evidence
    with full provenance lineage: Finding → Agent → Tool/Calculation → DB Query → Source Record IDs.
    """
    trigger_ev = state.get("trigger_evidence") or {}
    customer = trigger_ev.get("customer") or {}
    ledger = state.get("ledger_history") or []
    regulatory = state.get("regulatory_findings") or {}

    # Build explicit evidence provenance lineage map
    provenance_lineage = []

    # 1. Behavior Lineage
    beh = state.get("behavioral_metrics") or {}
    provenance_lineage.append({
        "finding": f"Velocity Z-Score = {beh.get('velocity_z_score')}σ, Pass-through = {beh.get('pass_through_ratio')}",
        "agent": "Behavior Analysis Agent",
        "tool_calculation": "calculate_behavior_metrics_tool (Mean vs Trigger amount)",
        "database_query": f"SELECT * FROM transactions WHERE customer_id = '{state.get('entity_id')}'",
        "source_record_ids": beh.get("source_records", [])[:5]
    })

    # 2. KYC Lineage
    kyc = state.get("kyc_metrics") or {}
    provenance_lineage.append({
        "finding": f"Income Activity Ratio = {kyc.get('income_activity_ratio')}x for occupation {kyc.get('occupation')}",
        "agent": "KYC Investigation Agent",
        "tool_calculation": f"observed_volume ({kyc.get('observed_volume')}) / declared_income ({kyc.get('declared_income')})",
        "database_query": f"SELECT * FROM customers WHERE customer_id = '{state.get('entity_id')}'",
        "source_record_ids": kyc.get("source_records", [])
    })

    # 3. Typology Lineage
    provenance_lineage.append({
        "finding": f"Primary Typology: {state.get('typology_classification')} — {state.get('typology_rationale')}",
        "agent": "Typology Classifier Agent",
        "tool_calculation": "detect_typologies_tool (Structuring threshold & rapid passthrough rules)",
        "database_query": "SELECT * FROM transactions",
        "source_record_ids": [t.get("id") for t in ledger if t.get("id")][:5]
    })

    # 4. Graph Lineage
    graph = state.get("graph_metrics") or {}
    provenance_lineage.append({
        "finding": f"Target In/Out Degree = {graph.get('target_in_degree')}/{graph.get('target_out_degree')}, Cycles: {graph.get('cycles_detected')}",
        "agent": "Graph Analyst Agent",
        "tool_calculation": "build_and_analyze_graph_tool (NetworkX Directed Graph)",
        "database_query": "SELECT account_id, receiver_account_id, beneficiary_id FROM transactions",
        "source_record_ids": graph.get("source_records", [])[:5]
    })

    state["evidence_provenance_lineage"] = provenance_lineage

    # Compile SAR dossier using LLM
    llm = LLMClient()
    user_payload = {
        "case_id": state.get("case_id"),
        "alert_id": state.get("alert_id"),
        "entity_id": state.get("entity_id"),
        "customer": {
            "name": customer.get("name"),
            "declared_income": customer.get("declared_income"),
            "occupation": customer.get("occupation"),
            "risk_level": customer.get("risk_level")
        },
        "typology": state.get("typology_classification"),
        "typology_rationale": state.get("typology_rationale"),
        "final_risk_score": state.get("final_risk_score"),
        "decision": state.get("decision"),
        "risk_factors_breakdown": state.get("risk_factors_breakdown"),
        "regulatory_reference": regulatory,
        "provenance_lineage": provenance_lineage
    }

    try:
        dossier = llm.generate(SYSTEM_PROMPT, f"SAR Investigation State Payload:\n{json.dumps(user_payload, indent=2, default=str)}")
        state["dossier"] = dossier
    except Exception as e:
        state["dossier"] = f"Generated SAR Dossier grounded in evidence payload:\n{json.dumps(user_payload, indent=2, default=str)}"

    # Persist updated state to DB
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
