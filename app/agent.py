from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
from operator import add
from api_client import *



llm = ChatOpenAI(model="gpt-4", 
                 api_key="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"
                 )

class AgentState(TypedDict):
    messages: Annotated[list, add]
    intent: str
    slug: str
    response: str

def detect_intent(state):
    message = state["messages"][-1]
    prompt = f"تشخیص intent از '{message}': service_selection, pricing, order_tracking, other"
    state["intent"] = llm.invoke(prompt).content.strip()
    return state

def handle_service(state):
    state["slug"] = get_service_slug(state["messages"][-1], llm)
    city_id = "1216"  # Default Tehran
    avail_msg = check_availability(state["slug"], city_id)
    if avail_msg:
        state["response"] = avail_msg
    else:
        state["response"] = f"سرویس {state['slug']} انتخاب شد."
    return state

def handle_pricing(state):
    if not state["slug"]:
        state = handle_service(state)
    state["response"] = get_pricing(state["slug"])
    return state

def handle_order(state):
    user_id = "dummy_user"
    token = "dummy_token"  # From auth
    orders = get_orders(user_id, token)
    state["response"] = f"وضعیت سفارش‌ها: {orders}"
    return state

def default_handler(state):
    state["response"] = "درک نکردم. لطفاً توضیح دهید."
    return state

graph = StateGraph(AgentState)
graph.add_node("detect_intent", detect_intent)
graph.add_node("handle_service", handle_service)
graph.add_node("handle_pricing", handle_pricing)
graph.add_node("handle_order", handle_order)
graph.add_node("default", default_handler)

# Edges based on intent
graph.add_conditional_edges("detect_intent", lambda s: s["intent"], {
    "service_selection": "handle_service",
    "pricing": "handle_pricing",
    "order_tracking": "handle_order",
    "other": "default"
})
graph.add_edge("handle_service", END)
graph.add_edge("handle_pricing", END)
graph.add_edge("handle_order", END)
graph.add_edge("default", END)

graph.set_entry_point("detect_intent")
agent = graph.compile()