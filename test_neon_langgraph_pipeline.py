import json
from app.database import SessionLocal
from app.repositories import AlertRepository
from app.agents.state import create_initial_state_from_neon_alert
from app.agents.graph import investigation_graph

def test_neon_to_langgraph_flow():
    print("=" * 70)
    print(" 🚀 NEON DB -> INVESTIGATION STATE -> LANGGRAPH FLOW TEST")
    print("=" * 70)

    db = SessionLocal()
    try:
        repo = AlertRepository(db)
        
        print("\n[1] FETCHING AND CLAIMING ONE OPEN ALERT FROM NEON DB...")
        enriched_alert = repo.fetch_and_claim_open_alert()

        if not enriched_alert:
            print("❌ No OPEN alerts found in Neon DB.")
            return

        alert_id = enriched_alert["alert"]["alert_id"]
        print(f" -> Claimed Alert ID: {alert_id}")
        print(f" -> Alert Type: {enriched_alert['alert']['alert_type']}")
        print(f" -> Status in DB: {enriched_alert['alert']['status']}")

        print("\n[2] CREATING INITIAL INVESTIGATION STATE...")
        initial_state = create_initial_state_from_neon_alert(enriched_alert)
        
        print(f" -> Case ID: {initial_state['case_id']}")
        print(f" -> Alert ID: {initial_state['alert_id']}")
        print(f" -> Entity ID: {initial_state['entity_id']}")
        print(f" -> Alert Type: {initial_state['alert_type']}")
        print(f" -> Priority Score: {initial_state['raw_priority_score']}")
        print(f" -> Trigger Evidence Keys: {list(initial_state['trigger_evidence'].keys())}")

        print("\n[3] INVOKING LANGGRAPH INVESTIGATION PIPELINE...")
        config = {"configurable": {"thread_id": initial_state["case_id"]}}
        final_state = investigation_graph.invoke(initial_state, config=config)

        print("\n[4] LANGGRAPH EXECUTION RESULT:")
        print(f" -> Plan Satisfied: {final_state.get('plan_satisfied')}")
        print(f" -> Investigation Plan Steps: {final_state.get('investigation_plan')}")
        print(f" -> Task List: {[t.get('name') + ':' + t.get('status') for t in final_state.get('task_list', [])]}")
        print(f" -> Missing Evidence: {final_state.get('missing_evidence')}")
        print(f" -> Ledger History Records: {len(final_state.get('ledger_history', []))}")
        print(f" -> KYC Notes: {final_state.get('kyc_notes')}")
        print(f" -> Derived Graph Metrics:\n{json.dumps(final_state.get('graph_metrics', {}), indent=2)}")

        print("\n✅ FLOW COMPLETED SUCCESSFULLY: Neon -> InvestigationState -> LangGraph")
        print("=" * 70)

    finally:
        db.close()

if __name__ == "__main__":
    test_neon_to_langgraph_flow()
