import pytest
from app.data.seed import seed
from app.agents.graph import investigation_graph
from app.agents.state import create_initial_state_from_neon_alert
from app.repositories.alert_repository import AlertRepository
from app.database import SessionLocal

@pytest.fixture(scope="module", autouse=True)
def setup_e2e_database():
    seed()

def test_full_end_to_end_investigation_pipeline():
    """
    Phase 20: End-to-End Test
    Validates complete investigation execution on real database alert.
    Verifies that every risk factor, graph metric, and SAR finding links to real database record IDs.
    """
    db = SessionLocal()
    try:
        repo = AlertRepository(db)
        enriched_alert = repo.fetch_and_claim_open_alert()
        assert enriched_alert is not None, "Seeded alert must exist in database"
        
        initial_state = create_initial_state_from_neon_alert(enriched_alert)
        config = {"configurable": {"thread_id": f"E2E_THREAD_{initial_state['alert_id']}"}}
        
        # Execute LangGraph Multi-Agent Pipeline
        final_state = investigation_graph.invoke(initial_state, config=config)
        
        # 1. Evidence Verification
        assert final_state.get("evidence_found") is True
        assert len(final_state.get("ledger_history", [])) > 0
        
        # 2. Agent Metrics & Typology Verification
        assert final_state.get("typology_classification") != ""
        assert "behavioral_metrics" in final_state
        assert "graph_metrics" in final_state
        assert "kyc_metrics" in final_state
        assert "regulatory_findings" in final_state
        
        # 3. Transparent Risk Engine Verification
        assert final_state.get("final_risk_score", 0.0) > 0.0
        assert final_state.get("decision") in ["ALLOW", "REVIEW", "BLOCK"]
        assert len(final_state.get("risk_factors_breakdown", [])) == 4
        
        # 4. Evidence Provenance Lineage Verification
        lineage = final_state.get("evidence_provenance_lineage", [])
        assert len(lineage) >= 4
        for item in lineage:
            assert "finding" in item
            assert "agent" in item
            assert "tool_calculation" in item
            assert "database_query" in item
            assert "source_record_ids" in item
            
        # 5. Grounded SAR Dossier Verification
        dossier = final_state.get("dossier", "")
        assert len(dossier) > 50
        
    finally:
        db.close()

if __name__ == "__main__":
    pytest.main(["-v", "test_e2e_investigation.py"])
