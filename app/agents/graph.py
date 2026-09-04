from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import InvestigationState
from .nodes.task_planner import task_planner_node
from .nodes.evidence_retrieval import evidence_retrieval_node
from .nodes.behavior_analyzer import behavior_analyzer_node
from .nodes.graph_analyst import graph_analyst_node
from .nodes.kyc_verifier import kyc_verifier_node
from .nodes.plan_checker import plan_checker_node

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
    Stops workflow execution at Plan Satisfaction Check (END).
    If unsatisfied and loop count < 2, retries missing tasks.
    """
    if state.get("plan_satisfied"):
        return END
    elif state.get("loop_count", 0) < 2:
        return "task_planner"
    else:
        return END

def create_investigation_graph():
    builder = StateGraph(InvestigationState)
    
    # 1. Add Task Planning & Evidence Gathering Nodes
    builder.add_node("task_planner", task_planner_node)
    builder.add_node("evidence_retrieval", evidence_retrieval_node)
    builder.add_node("behavior_analyzer", behavior_analyzer_node)
    builder.add_node("graph_analyst", graph_analyst_node)
    builder.add_node("kyc_verifier", kyc_verifier_node)
    builder.add_node("plan_checker", plan_checker_node)
    
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
    
    # Plan Satisfaction Router -> Ends at plan_checker
    builder.add_conditional_edges(
        "plan_checker",
        route_on_plan_satisfaction,
        {
            "task_planner": "task_planner",
            END: END
        }
    )
    
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)

# Global graph instance
investigation_graph = create_investigation_graph()
