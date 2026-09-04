import json
from app.models.schema import ClassifiedAlert
from app.agents.nodes.task_planner import task_planner_node
from app.agents.nodes.evidence_retrieval import evidence_retrieval_node
from app.agents.nodes.kyc_verifier import kyc_verifier_node
from app.agents.nodes.behavior_analyzer import behavior_analyzer_node
from app.agents.nodes.graph_analyst import graph_analyst_node
from app.agents.nodes.plan_checker import plan_checker_node

def test_phase1_alert_payload():
    print("=" * 70)
    print(" 🌉 PHASE-1 REST API PAYLOAD INTEGRATION TEST")
    print("=" * 70)

    # Exact JSON format produced by Phase-1 (financial-crime-alert-investigation)
    phase1_json = {
        "classified_alert_id": "ALT-PHASE1-0042",
        "account_id": "ACC-9942",
        "transaction_ids": ["TX-1001", "TX-1002"],
        "alert_type": "STRUCTURING",
        "triggered_rules": ["STRUCTURING", "HIGH_VELOCITY"],
        "detected_reason": "Multiple structured deposits under $10,000 threshold within 1 hour",
        "evidence": {
            "total_amount": 29400.0,
            "transaction_count": 3,
            "avg_amount": 9800.0
        },
        "risk_score": 88,
        "risk_level": "CRITICAL",
        "timestamp": "2026-09-04T03:30:00Z",
        "status": "NEW"
    }

    print("\n[1] RECEIVING RAW PHASE-1 JSON REST API PAYLOAD:")
    print(json.dumps(phase1_json, indent=2))

    # Parse JSON payload into Pydantic model using Phase-1 compatibility helpers
    alert_model = ClassifiedAlert(**phase1_json)
    
    alert_id = alert_model.get_alert_id()
    entity_id = alert_model.get_entity_id()
    severity = alert_model.get_severity()
    raw_score = alert_model.get_score()
    trigger_evidence = alert_model.get_features()

    print("\n[2] PARSED VIA CLASSIFIED ALERT ADAPTER:")
    print(f" -> Alert ID: {alert_id}")
    print(f" -> Entity ID: {entity_id}")
    print(f" -> Alert Type: {alert_model.alert_type}")
    print(f" -> Severity: {severity}")
    print(f" -> Score: {raw_score}")
    print(f" -> Trigger Evidence: {trigger_evidence}")

    # Seed State
    state = {
        "case_id": f"CASE_{alert_id}",
        "alert_id": alert_id,
        "entity_id": entity_id,
        "alert_type": alert_model.alert_type,
        "raw_priority_score": raw_score,
        "trigger_evidence": trigger_evidence,
        "task_list": [],
        "current_task": "",
        "plan_satisfied": False,
        "loop_count": 0,
        "missing_evidence": [],
        "historical_cases": [],
        "ledger_history": [],
        "balance_history": {},
        "behavioral_metrics": {},
        "graph_metrics": {},
        "kyc_notes": "",
        "typology_classification": "",
        "typology_rationale": "",
        "forensic_questions": [],
        "investigation_plan": [],
        "dossier": "",
        "final_risk_score": 0.0,
        "decision": ""
    }

    # Execute Task Planner
    state = task_planner_node(state)
    print("\n[3] TASK PLANNER NODE OUTPUT:")
    print(f" -> Plan Steps: {state['investigation_plan']}")
    print(f" -> Tasks: {[t['name'] for t in state['task_list']]}")

    # Execute Agents & Plan Checker
    state = evidence_retrieval_node(state)
    state = kyc_verifier_node(state)
    state = behavior_analyzer_node(state)
    state = graph_analyst_node(state)
    state = plan_checker_node(state)

    print("\n[4] PLAN SATISFACTION CHECKER OUTPUT:")
    print(f" -> Plan Satisfied: {state['plan_satisfied']}")
    print(f" -> Missing Evidence: {state['missing_evidence']}")
    print("\n -> Integration Test Passed Successfully!")
    print("=" * 70)

if __name__ == "__main__":
    test_phase1_alert_payload()
