from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import InvestigationState
from .nodes.task_planner import task_planner_node
from .nodes.evidence_retrieval import evidence_retrieval_node
from .nodes.behavior_analyzer import behavior_analyzer_node
from .nodes.graph_analyst import graph_analyst_node
from .nodes.kyc_verifier import kyc_verifier_node
from .nodes.plan_checker import plan_checker_node
from .nodes.typology_classifier import typology_classifier_node
from .nodes.regulatory_agent import regulatory_agent_node
from .nodes.scoring_node import scoring_node
from .nodes.case_assembler import case_assembler_node

def route_next_task(state: InvestigationState):
    """
    Examines task_list and routes to the agent handling the next PENDING task.
    If all tasks are completed, routes to plan_checker.
    """
    task_list = state.get("task_list", [])
    for task in task_list:
        if task.get("status") == "PENDING":
            name = task.get("name")
            if name == "FETCH_EVIDENCE":
                return "evidence_retrieval"
            elif name == "VERIFY_KYC":
                return "kyc_verifier"
            elif name == "ANALYZE_BEHAVIOR":
                return "behavior_analyzer"
            elif name == "ANALYZE_GRAPH":
                return "graph_analyst"
    return "plan_checker"

def route_on_plan_satisfaction(state: InvestigationState):
    """
    Routes to typology_classifier once plan is satisfied or loop limit reached.
    """
    if state.get("plan_satisfied"):
        return "typology_classifier"
    elif state.get("loop_count", 0) < 2:
        return "task_planner"
    else:
        return "typology_classifier"

def create_investigation_graph():
    builder = StateGraph(InvestigationState)
    
    # 1. Add All Pipeline Nodes
    builder.add_node("task_planner", task_planner_node)
    builder.add_node("evidence_retrieval", evidence_retrieval_node)
    builder.add_node("behavior_analyzer", behavior_analyzer_node)
    builder.add_node("graph_analyst", graph_analyst_node)
    builder.add_node("kyc_verifier", kyc_verifier_node)
    builder.add_node("plan_checker", plan_checker_node)
    builder.add_node("typology_classifier", typology_classifier_node)
    builder.add_node("regulatory_agent", regulatory_agent_node)
    builder.add_node("scoring_node", scoring_node)
    builder.add_node("case_assembler", case_assembler_node)
    
    # Entry Point: Task Planner studies alert JSON and generates task_list
    builder.set_entry_point("task_planner")
    
    # Router map for task execution loop
    task_routes = {
        "evidence_retrieval": "evidence_retrieval",
        "kyc_verifier": "kyc_verifier",
        "behavior_analyzer": "behavior_analyzer",
        "graph_analyst": "graph_analyst",
        "plan_checker": "plan_checker"
    }
    
    # Dynamic Task Routing Loop
    builder.add_conditional_edges("task_planner", route_next_task, task_routes)
    builder.add_conditional_edges("evidence_retrieval", route_next_task, task_routes)
    builder.add_conditional_edges("kyc_verifier", route_next_task, task_routes)
    builder.add_conditional_edges("behavior_analyzer", route_next_task, task_routes)
    builder.add_conditional_edges("graph_analyst", route_next_task, task_routes)
    
    # Plan Satisfaction Router -> Routes to typology_classifier
    builder.add_conditional_edges(
        "plan_checker",
        route_on_plan_satisfaction,
        {
            "task_planner": "task_planner",
            "typology_classifier": "typology_classifier"
        }
    )
    
    # Linear Downstream Sequence: Typology -> Regulatory -> Scoring -> Case Assembler -> END
    builder.add_edge("typology_classifier", "regulatory_agent")
    builder.add_edge("regulatory_agent", "scoring_node")
    builder.add_edge("scoring_node", "case_assembler")
    builder.add_edge("case_assembler", END)
    
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)

# Global graph instance
investigation_graph = create_investigation_graph()
