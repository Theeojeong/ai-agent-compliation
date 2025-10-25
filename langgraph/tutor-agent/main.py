from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END, MessagesState
from agents.classification_agent import classification_agent
from agents.feynman_agent import feynman_agent
from agents.teacher_agent import teacher_agent
from agents.quiz_agent import quiz_agent


class TutorState(MessagesState):
    current_agent: str


def router_check(state: TutorState):
    route = state.get("current_agent", "classification_agent")

    return route


graph_builder = StateGraph(TutorState)

# =======노드========

graph_builder.add_node(
    "classification_agent",
    classification_agent,
    destinations=(
        "feynman_agent",
        "teacher_agent",
        "quiz_agent",
    ),
)
graph_builder.add_node("feynman_agent", feynman_agent)
graph_builder.add_node("teacher_agent", teacher_agent)
graph_builder.add_node("quiz_agent", quiz_agent)

# =======엣지========

graph_builder.add_conditional_edges(
    START,
    router_check,
    [
        "classification_agent",
        "feynman_agent",
        "teacher_agent",
        "quiz_agent",
    ],
)
graph_builder.add_edge("classification_agent", END)

graph = graph_builder.compile()
