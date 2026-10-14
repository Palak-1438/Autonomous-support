from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from app.schemas.orchestration import ClassificationResult, SpecialistResult, SupervisorDecision
from app.orchestration.provider import get_provider

class GraphState(TypedDict):
    content: str
    classification: Optional[ClassificationResult]
    specialist: Optional[SpecialistResult]
    supervisor: Optional[SupervisorDecision]
    response_content: Optional[str]
    escalated: bool

def route_node(state: GraphState) -> GraphState:
    provider = get_provider()
    classification = provider.classify(state["content"])
    return {"classification": classification}

def process_node(state: GraphState) -> GraphState:
    provider = get_provider()
    specialist = provider.process(state["content"], state["classification"])
    return {"specialist": specialist}

def supervise_node(state: GraphState) -> GraphState:
    provider = get_provider()
    supervisor = provider.supervise(state["content"], state["specialist"])

    # We don't return response_content here since it is set on edges / end
    return {"supervisor": supervisor}

def escalate_node(state: GraphState) -> GraphState:
    return {
        "response_content": "Escalated to human.",
        "escalated": True
    }

def format_response_node(state: GraphState) -> GraphState:
    # Final successful response format
    return {
        "response_content": state["supervisor"].approved_answer or state["specialist"].proposed_answer,
        "escalated": False
    }

def should_escalate_after_route(state: GraphState) -> str:
    if state["classification"].selected_specialist == "human_handoff":
        return "escalate"
    return "process"

def should_escalate_after_supervise(state: GraphState) -> str:
    if state["supervisor"].outcome == "ESCALATE":
        return "escalate"
    return "format"


# Build the graph
workflow = StateGraph(GraphState)

workflow.add_node("route", route_node)
workflow.add_node("process", process_node)
workflow.add_node("supervise", supervise_node)
workflow.add_node("escalate", escalate_node)
workflow.add_node("format", format_response_node)

workflow.set_entry_point("route")

workflow.add_conditional_edges(
    "route",
    should_escalate_after_route,
    {
        "process": "process",
        "escalate": "escalate"
    }
)

workflow.add_edge("process", "supervise")

workflow.add_conditional_edges(
    "supervise",
    should_escalate_after_supervise,
    {
        "format": "format",
        "escalate": "escalate"
    }
)

workflow.add_edge("escalate", END)
workflow.add_edge("format", END)

app_graph = workflow.compile()
