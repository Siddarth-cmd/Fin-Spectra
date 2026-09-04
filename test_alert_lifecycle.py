from unittest.mock import patch
from app.database import SessionLocal
from app.models.schema import Alert, InvestigationCase
from app.repositories import AlertRepository
from app.agents.state import create_initial_state_from_neon_alert
from app.agents.graph import investigation_graph
from run_investigation_demo import fetch_read_only_alert, DummySession

def test_alert_lifecycle_transitions():
    print("=" * 70)
    print(" 🧪 TESTING ALERT & INVESTIGATION CASE LIFECYCLE TRANSITIONS")
    print("=" * 70)

    db = SessionLocal()
    try:
        repo = AlertRepository(db)

        # 1. Test Safe Mode Read-Only Protection
        print("\n[1] TESTING SAFE MODE READ-ONLY PROTECTION...")
        open_alert_read = fetch_read_only_alert(db)
        if not open_alert_read:
            print(" ⚠️  No OPEN alerts available for lifecycle testing.")
            return

        target_alert_id = open_alert_read["alert"]["alert_id"]
        initial_db_alert = db.query(Alert).filter(Alert.alert_id == target_alert_id).first()
        initial_status = initial_db_alert.status
        assert initial_status == "OPEN", f"Expected initial status OPEN, got {initial_status}"
        print(f" -> Safe mode target Alert ID: {target_alert_id} (Status: {initial_status})")

        # Run state creation and graph under safe mode patch
        initial_state = create_initial_state_from_neon_alert(open_alert_read)
        config = {"configurable": {"thread_id": initial_state["case_id"]}}

        with patch("app.database.SessionLocal", DummySession), \
             patch("app.agents.nodes.scoring_node.SessionLocal", DummySession):
            final_state = investigation_graph.invoke(initial_state, config=config)

        db.refresh(initial_db_alert)
        case_in_db = db.query(InvestigationCase).filter(InvestigationCase.id == initial_state["case_id"]).first()

        assert initial_db_alert.status == "OPEN", f"Safe mode mutated alert status to {initial_db_alert.status}!"
        assert case_in_db is None, "Safe mode persisted an InvestigationCase!"
        print(" ✓ Safe mode verified: Alert status remains OPEN and zero DB mutations occurred.")

        # 2. Test Claim Path (OPEN -> UNDER_INVESTIGATION)
        print("\n[2] TESTING CLAIM PATH (OPEN -> UNDER_INVESTIGATION)...")
        claimed_alert_data = repo.fetch_and_claim_open_alert()
        assert claimed_alert_data is not None, "Failed to claim an OPEN alert!"
        claimed_id = claimed_alert_data["alert"]["alert_id"]
        
        claimed_db_alert = db.query(Alert).filter(Alert.alert_id == claimed_id).first()
        assert claimed_db_alert.status == "UNDER_INVESTIGATION", f"Expected status UNDER_INVESTIGATION, got {claimed_db_alert.status}"
        print(f" -> Claimed Alert ID: {claimed_id} | Status in DB: {claimed_db_alert.status}")
        print(" ✓ Claim path verified: OPEN -> UNDER_INVESTIGATION.")

        # 3. Test Failure Path (Simulated Error -> FAILED, NOT CLOSED)
        print("\n[3] TESTING FAILURE PATH (SIMULATED ERROR -> FAILED)...")
        repo.fail_alert(claimed_id, new_status="FAILED")
        failed_db_alert = db.query(Alert).filter(Alert.alert_id == claimed_id).first()
        assert failed_db_alert.status == "FAILED", f"Expected status FAILED, got {failed_db_alert.status}"
        assert failed_db_alert.status != "CLOSED", "Failed alert was erroneously marked CLOSED!"
        print(f" -> Failed Alert ID: {claimed_id} | Status in DB: {failed_db_alert.status}")
        print(" ✓ Failure path verified: Alert set to FAILED and NOT CLOSED.")

        # 4. Test Success Path (OPEN -> UNDER_INVESTIGATION -> Graph -> InvestigationCase CLOSED -> Alert CLOSED)
        print("\n[4] TESTING COMPLETE SUCCESS PATH (OPEN -> UNDER_INVESTIGATION -> CLOSED)...")
        success_alert_data = repo.fetch_and_claim_open_alert()
        assert success_alert_data is not None, "Failed to claim next OPEN alert!"
        success_id = success_alert_data["alert"]["alert_id"]

        success_state = create_initial_state_from_neon_alert(success_alert_data)
        config_succ = {"configurable": {"thread_id": success_state["case_id"]}}
        final_succ_state = investigation_graph.invoke(success_state, config=config_succ)

        persisted_case = db.query(InvestigationCase).filter(InvestigationCase.id == success_state["case_id"]).first()
        assert persisted_case is not None, "InvestigationCase not persisted!"
        assert persisted_case.status == "CLOSED", f"Expected InvestigationCase status CLOSED, got {persisted_case.status}"

        # Complete Alert lifecycle after successful InvestigationCase persistence
        repo.complete_alert(success_id)
        final_db_alert = db.query(Alert).filter(Alert.alert_id == success_id).first()
        assert final_db_alert.status == "CLOSED", f"Expected Alert status CLOSED, got {final_db_alert.status}"

        print(f" -> Alert ID: {success_id} | Status in 'alerts' table: {final_db_alert.status}")
        print(f" -> Case ID : {persisted_case.id} | Status in 'investigation_cases' table: {persisted_case.status}")
        print(" ✓ Full success path verified: Alert = CLOSED and InvestigationCase = CLOSED.")

        print("\n" + "=" * 70)
        print("✅ ALL ALERT LIFECYCLE TESTS PASSED PERFECTLY!")
        print("=" * 70)

    finally:
        db.close()

if __name__ == "__main__":
    test_alert_lifecycle_transitions()
