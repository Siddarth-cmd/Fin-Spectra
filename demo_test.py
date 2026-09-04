import json
from app.agents.nodes.task_planner import task_planner_node
from app.agents.nodes.evidence_retrieval import evidence_retrieval_node
from app.agents.nodes.kyc_verifier import kyc_verifier_node
from app.agents.nodes.behavior_analyzer import behavior_analyzer_node
from app.agents.nodes.graph_analyst import graph_analyst_node
from app.agents.nodes.plan_checker import plan_checker_node

def run_demo_investigation(alert_payload: dict):
    print("=" * 70)
    print(" 🚀 FINSPECTRA ENGINE DEMO: TASK-DRIVEN INVESTIGATION WORKFLOW")
    print("=" * 70)
    
    # 1. Incoming Request Payload
    print("\n[1] RECEIVING INCOMING ALERT JSON REQUEST:")
    print(json.dumps(alert_payload, indent=2))
    
    # Initialize State Memory
    state = {
        "case_id": f"CASE_{alert_payload['alert_id']}",
        "alert_id": alert_payload["alert_id"],
        "entity_id": alert_payload["entity_id"],
        "alert_type": alert_payload["alert_type"],
        "raw_priority_score": alert_payload["raw_score"],
        "trigger_evidence": alert_payload["features_json"],
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

    # 2. Upfront Task Planner Node
    print("\n[2] EXECUTING TASK PLANNER NODE...")
    state = task_planner_node(state)
    print(f" -> Alert Type Analyzed: {state['alert_type']}")
    print(" -> Generated Static Investigation Plan:")
    for step in state["investigation_plan"]:
        print(f"    • {step}")
    print(" -> Generated Task Queue:")
    print(json.dumps(state["task_list"], indent=2))

    # 3. Executing Task-Driven Evidence Agents
    print("\n[3] ROUTING TASKS TO SPECIALIZED EVIDENCE AGENTS...")
    
    # Task 1: Fetch Evidence
    print("\n   [Agent: Evidence Retrieval]")
    # Seed mock ledger for demo
    state["ledger_history"] = [
        {"id": "TX_101", "dir": "IN", "amount": 25000.0, "channel": "Wire", "time": "2026-09-04T01:00:00"},
        {"id": "TX_102", "dir": "OUT", "amount": 24800.0, "channel": "ACH", "time": "2026-09-04T01:05:00"}
    ]
    state["kyc_notes"] = "Type: Savings, Occupation: Software Engineer"
    for t in state["task_list"]:
        if t["name"] == "FETCH_EVIDENCE": t["status"] = "COMPLETED"
    print("   -> Status: FETCH_EVIDENCE marked COMPLETED")

    # Task 2: KYC Verifier
    print("\n   [Agent: KYC Verifier]")
    state = kyc_verifier_node(state)
    print(f"   -> KYC Notes Updated: {state['kyc_notes']}")

    # Task 3: Behavior Analyzer
    print("\n   [Agent: Behavior Analyzer]")
    state = behavior_analyzer_node(state)
    print(f"   -> Behavioral Metrics: {json.dumps(state['behavioral_metrics'], indent=2)}")

    # Task 4: Graph Analyst
    print("\n   [Agent: Graph Analyst]")
    state = graph_analyst_node(state)
    print(f"   -> Graph Metrics: {json.dumps(state['graph_metrics'], indent=2)}")

    # 4. Plan Satisfaction Checker
    print("\n[4] EXECUTING PLAN SATISFACTION CHECKER NODE...")
    state = plan_checker_node(state)
    print(f" -> Plan Satisfied Status: {state['plan_satisfied']}")
    print(f" -> Missing Evidence: {state['missing_evidence']}")

    # 5. Terminal Response
    print("\n[5] TERMINAL WORKFLOW RESPONSE (ENGINE STOPS AT PLAN CHECK):")
    response_payload = {
        "status": "plan_check_completed",
        "case_id": state["case_id"],
        "entity_id": state["entity_id"],
        "plan_satisfied": state["plan_satisfied"],
        "task_list": state["task_list"],
        "investigation_plan": state["investigation_plan"],
        "missing_evidence": state["missing_evidence"],
        "collected_evidence_summary": {
            "ledger_records": len(state["ledger_history"]),
            "kyc_notes": state["kyc_notes"],
            "behavioral_metrics": state["behavioral_metrics"],
            "graph_metrics": state["graph_metrics"]
        }
    }
    print(json.dumps(response_payload, indent=2))
    print("\n" + "=" * 70)

if __name__ == "__main__":
    sample_request = {
        "alert_id": "ALT_89201",
        "entity_id": "ACC_4091",
        "alert_type": "RAPID_PASS_THROUGH",
        "severity": "CRITICAL",
        "raw_score": 0.94,
        "priority_rank": 1,
        "trigger_reason": "Inflow of $25,000 immediately transferred out in 5 minutes",
        "features_json": {
            "inflow_amount": 25000.0,
            "outflow_amount": 24800.0,
            "time_window_minutes": 5
        }
    }
    run_demo_investigation(sample_request)
