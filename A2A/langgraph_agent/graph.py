from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain.chat_models import init_chat_model

load_dotenv()

class State(MessagesState):
    pass

graph_builder = StateGraph(State)

llm = init_chat_model("gpt-4o")

def call_model(state: State):
    response = llm.invoke(state['messages'])
    return {"messages": response}

graph_builder.add_node("call_model", call_model)
graph_builder.add_edge(START, "call_model",)
graph_builder.add_edge("call_model", END)

graph = graph_builder.compile()

