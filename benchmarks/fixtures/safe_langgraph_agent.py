"""LangGraph research agent with an explicit recursion budget and durable state."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph


def call_model(state: dict) -> dict:
    return {"messages": state["messages"] + [llm.invoke(state["messages"])]}


def call_tools(state: dict) -> dict:
    return {"messages": state["messages"] + [run_tool(state["messages"][-1])]}


def should_continue(state: dict) -> str:
    return "tools" if state["messages"][-1].tool_calls else END


builder = StateGraph(dict)
builder.add_node("model", call_model)
builder.add_node("tools", call_tools)
builder.add_edge(START, "model")
builder.add_conditional_edges("model", should_continue)
builder.add_edge("tools", "model")

graph = builder.compile(checkpointer=MemorySaver())
result = graph.invoke(
    {"messages": []},
    config={"recursion_limit": 12, "configurable": {"thread_id": "research-1"}},
)
