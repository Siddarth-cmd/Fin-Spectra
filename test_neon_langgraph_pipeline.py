import json
from app.database import SessionLocal
from app.repositories import AlertRepository
from app.agents.state import create_initial_state_from_neon_alert
from app.agents.graph import investigation_graph
from app.models.schema import InvestigationCase

def test_neon_to_langgraph_full_pipeline():
    print("=" * 70)
    print(" 🚀 NEON DB -> INVESTIGATION STATE -> LANGGRAPH COMPLETE FLOW TEST")
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

        print("\n[3] INVOKING LANGGRAPH INVESTIGATION PIPELINE...")
        config = {"configurable": {"thread_id": initial_state["case_id"]}}
        final_state = investigation_graph.invoke(initial_state, config=config)

        print("\n[4] VERIFYING NEON DB PERSISTENCE OF INVESTIGATION CASE & SNAPSHOT...")
        saved_case = db.query(InvestigationCase).filter(InvestigationCase.id == final_state["case_id"]).first()
        snapshot = saved_case.state_snapshot_json if saved_case else {}

        behavior = final_state.get("behavioral_metrics", {})
        subscores = behavior.get("risk_subscores", {})

        print("\n" + "=" * 70)
        print(" 📊 COMPLETE PIPELINE OUTPUT SUMMARY")
        print("=" * 70)
        print(f" -> Alert ID:                {final_state.get('alert_id')}")
        print(f" -> Plan Satisfied:          {final_state.get('plan_satisfied')}")
        print(f" -> Typology Classification: {final_state.get('typology_classification')}")
        print(f" -> Typology Rationale:      {final_state.get('typology_rationale')[:120]}...")
        print(f" -> Subscores:               {json.dumps(subscores)}")
        print(f" -> Final Risk Score:        {final_state.get('final_risk_score')}")
        print(f" -> Decision:                {final_state.get('decision')}")
        print(f" -> Dossier Snippet:\n{final_state.get('dossier')[:200]}...")
        print("=" * 70)
        print(" 💾 NEON DB PERSISTED SNAPSHOT VERIFICATION:")
        print(f" -> DB Typology in Snapshot: {snapshot.get('typology_classification')}")
        print(f" -> DB Decision in Snapshot: {snapshot.get('decision')}")
        print(f" -> DB Dossier in Snapshot:  {bool(snapshot.get('dossier'))}")
        print("=" * 70)

        # Assertions
        assert saved_case is not None, "InvestigationCase record was not persisted to Neon DB!"
        assert saved_case.decision == final_state["decision"], "Persisted decision does not match final_state!"
        assert "typology_classification" in snapshot, "Missing typology_classification in DB snapshot!"
        assert "dossier" in snapshot, "Missing dossier in DB snapshot!"

        print("\n✅ COMPLETE PIPELINE VERIFIED SUCCESSFULLY WITH ZERO ERRORS!")
        print("=" * 70)

    finally:
        db.close()

if __name__ == "__main__":
    test_neon_to_langgraph_full_pipeline()
