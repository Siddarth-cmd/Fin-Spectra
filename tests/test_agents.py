import pytest
from app.database import SessionLocal
from app.data.seed import seed
from app.agents.tools import (
    get_customer_tool,
    get_transactions_tool,
    calculate_behavior_metrics_tool,
    detect_typologies_tool,
    build_and_analyze_graph_tool,
    get_regulatory_guidance_tool
)
from app.agents.nodes.evidence_retrieval import evidence_retrieval_node
from app.agents.nodes.kyc_verifier import kyc_verifier_node
from app.agents.nodes.behavior_analyzer import behavior_analyzer_node
from app.agents.nodes.graph_analyst import graph_analyst_node
from app.agents.nodes.typology_classifier import typology_classifier_node
from app.agents.nodes.scoring_node import scoring_node

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    seed()

def test_evidence_retrieval_agent():
    state = {
        "entity_id": "CUST-1001",
        "case_id": "TEST_CASE_1",
        "alert_id": "ALT-4001",
        "trigger_evidence": {},
        "task_list": [{"name": "FETCH_EVIDENCE", "status": "PENDING"}]
    }
    res = evidence_retrieval_node(state)
    assert res["evidence_found"] is True
    assert len(res["ledger_history"]) > 0
    assert res["trigger_evidence"]["customer"]["customer_id"] == "CUST-1001"
    assert res["task_list"][0]["status"] == "COMPLETED"

def test_kyc_investigation_agent():
    state = {
        "entity_id": "CUST-3001",
        "trigger_evidence": {
            "customer": {
                "customer_id": "CUST-3001",
                "declared_income": 250000.0,
                "occupation": "Student",
                "risk_level": "CRITICAL",
                "account_age_days": 45
            }
        },
        "behavioral_metrics": {"total_volume_in": 5000000.0, "total_volume_out": 4920000.0},
        "ledger_history": [],
        "task_list": [{"name": "VERIFY_KYC", "status": "PENDING"}]
    }
    res = kyc_verifier_node(state)
    metrics = res["kyc_metrics"]
    assert metrics["income_activity_ratio"] >= 15.0
    assert "ALERT" in metrics["verdict_summary"]

def test_behavior_analysis_agent():
    state = {
        "entity_id": "CUST-2001",
        "trigger_evidence": {"transaction": {"transaction_id": "TXN-STRUCT-5", "amount": 999000.0}},
        "ledger_history": [
            {"id": "TXN-1", "transaction_id": "TXN-1", "amount": 2500.0, "dir": "IN"},
            {"id": "TXN-2", "transaction_id": "TXN-2", "amount": 2500.0, "dir": "IN"},
            {"id": "TXN-3", "transaction_id": "TXN-3", "amount": 2500.0, "dir": "IN"},
            {"id": "TXN-4", "transaction_id": "TXN-4", "amount": 2500.0, "dir": "IN"},
            {"id": "TXN-STRUCT-5", "transaction_id": "TXN-STRUCT-5", "amount": 999000.0, "dir": "IN"}
        ],
        "task_list": [{"name": "ANALYZE_BEHAVIOR", "status": "PENDING"}]
    }
    res = behavior_analyzer_node(state)
    beh = res["behavioral_metrics"]
    assert beh["historical_transaction_count"] == 4
    assert beh["velocity_z_score"] > 0.0

def test_typology_detection_agent():
    txs = [
        {"transaction_id": f"TXN-STR-{i}", "amount": 990000.0 + i*1000, "customer_id": "CUST-2001"}
        for i in range(3)
    ]
    det = detect_typologies_tool(txs, "CUST-2001")
    assert "STRUCTURING" in det["all_detected_typologies"]

def test_graph_analysis_agent():
    state = {
        "entity_id": "CUST-1001",
        "task_list": [{"name": "ANALYZE_GRAPH", "status": "PENDING"}]
    }
    res = graph_analyst_node(state)
    g = res["graph_metrics"]
    assert g["account_count"] > 0
    assert "source_records" in g

def test_risk_scoring_engine():
    state = {
        "case_id": "CASE_ALT_TEST",
        "alert_id": "ALT_TEST",
        "entity_id": "CUST-3001",
        "behavioral_metrics": {"velocity_z_score": 4.5},
        "kyc_metrics": {"income_activity_ratio": 19.68},
        "detected_typology_evidence": {"RAPID_PASS_THROUGH": {}},
        "graph_metrics": {"cycles_detected": True, "target_in_degree": 2, "target_out_degree": 2},
        "typology_classification": "RAPID_PASS_THROUGH"
    }
    res = scoring_node(state)
    assert res["final_risk_score"] > 75.0
    assert res["decision"] == "BLOCK"
    assert len(res["risk_factors_breakdown"]) == 4
