import json
import os
import boto3

from langchain.agents import create_agent
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import AIMessage, AnyMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.environ["MODEL_ID"]
RECOMMEND_FUNCTION = os.environ["RECOMMEND_FUNCTION"]
PLACE_ORDER_FUNCTION = os.environ["PLACE_ORDER_FUNCTION"]
ORDER_STATUS_FUNCTION = os.environ["ORDER_STATUS_FUNCTION"]

lambda_client = boto3.client("lambda", region_name=AWS_REGION)


def invoke_lambda(function_name: str, payload: dict) -> dict:
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode("utf-8"),
    )
    result = json.loads(response["Payload"].read())
    if response.get("FunctionError"):
        return {
            "ok": False,
            "error": "tool_invocation_failed",
            "message": str(result),
        }
    return result


@tool
def recommend_products(prompt: str) -> dict:
    """Suggest products using the AnyCart catalog knowledge base."""
    return invoke_lambda(RECOMMEND_FUNCTION, {"prompt": prompt})


@tool
def place_order(product_id: str, quantity: int, confirmed: bool, idempotency_key: str) -> dict:
    """Create an order only after explicit shopper confirmation."""
    return invoke_lambda(
        PLACE_ORDER_FUNCTION,
        {
            "product_id": product_id,
            "quantity": quantity,
            "confirmed": confirmed,
            "idempotency_key": idempotency_key,
        },
    )


@tool
def get_order(order_id: str) -> dict:
    """Retrieve one order by its order ID."""
    return invoke_lambda(ORDER_STATUS_FUNCTION, {"order_id": order_id})


model = ChatBedrockConverse(model=MODEL_ID, region_name=AWS_REGION)


class State(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    intent: str
    product_id: str
    quantity: int
    order_id: str
    confirmed: bool
    idempotency_key: str
    error: str


ORCHESTRATOR_PROMPT = """
You are the AnyCart orchestrator.
Return only a JSON object with these keys:
{
  "intent": "recommend|order|track|unsupported",
  "product_id": "",
  "quantity": 1,
  "order_id": ""
}

Rules:
- Use "order" only when the shopper explicitly asks to buy or order and supplies a product ID.
- Use "track" when the shopper asks for an order status and supplies an order ID.
- Use "recommend" for product discovery or browsing requests related to AnyCart products.
- Use "unsupported" for requests unrelated to recommendation, ordering, or order tracking.
- Do not create confirmation or idempotency values.
""".strip()

VALID_INTENTS = {"recommend", "order", "track", "unsupported"}


def parse_orchestrator_response(content: str) -> dict:
    try:
        parsed = json.loads(content)
    except (TypeError, json.JSONDecodeError):
        return {"intent": "invalid", "error": "The orchestrator returned malformed routing data."}

    intent = str(parsed.get("intent", "")).strip().lower()
    if intent not in VALID_INTENTS:
        return {"intent": "invalid", "error": f"Unsupported intent: {intent or 'missing'}."}

    try:
        quantity = int(parsed.get("quantity", 1))
    except (TypeError, ValueError):
        return {"intent": "invalid", "error": "The requested quantity was not an integer."}

    product_id = str(parsed.get("product_id", "")).strip()
    order_id = str(parsed.get("order_id", "")).strip()

    if intent == "order" and not product_id:
        return {"intent": "invalid", "error": "An order request must include a product ID."}
    if intent == "track" and not order_id:
        return {"intent": "invalid", "error": "An order-tracking request must include an order ID."}
    if intent == "order" and not 1 <= quantity <= 10:
        return {"intent": "invalid", "error": "Order quantity must be between 1 and 10."}
    if intent == "unsupported":
        return {"intent": "unsupported", "error": "I can help with product recommendations, orders, and order tracking."}

    return {
        "intent": intent,
        "product_id": product_id,
        "quantity": quantity,
        "order_id": order_id,
        "error": "",
    }


def orchestrator(state: State) -> dict:
    response = model.invoke([SystemMessage(content=ORCHESTRATOR_PROMPT)] + state["messages"])
    return parse_orchestrator_response(str(response.text))


def route_to_worker(state: State) -> str:
    intent = state.get("intent", "invalid")
    if intent == "recommend":
        return "recommendation_agent"
    if intent == "order":
        return "order_management_node"
    if intent == "track":
        return "order_tracking_node"
    return "input_error_node"


_recommendation_agent = create_agent(
    model=model,
    tools=[recommend_products],
    system_prompt=(
        "You are the AnyCart recommendation agent. Use the recommend_products tool for catalog information. "
        "Present each matching product with its exact product name, product_id, price, and a short description. "
        "Do not invent product IDs or products that are absent from the tool result."
    ),
)


def recommendation_agent(state: State) -> dict:
    result = _recommendation_agent.invoke({"messages": state["messages"]})
    return {"messages": [result["messages"][-1]]}


def order_management_node(state: State) -> dict:
    product_id = state.get("product_id", "")
    quantity = state.get("quantity", 1)
    confirmed = state.get("confirmed", False)
    idempotency_key = state.get("idempotency_key", "")

    if not confirmed:
        return {"messages": [AIMessage(content="I have the order details, but the purchase has not been explicitly confirmed. Confirm the purchase before the order is created.")]}
    if not idempotency_key:
        return {"messages": [AIMessage(content="The confirmed order is missing a request identifier.")]}

    result = place_order.invoke({
        "product_id": product_id,
        "quantity": quantity,
        "confirmed": True,
        "idempotency_key": idempotency_key,
    })
    if not result.get("ok", False):
        return {"messages": [AIMessage(content=result.get("message", "The order could not be created."))]}

    duplicate_note = " This was a safe retry." if result.get("duplicate") else ""
    return {"messages": [AIMessage(content=f"Order {result['order_id']} was accepted with status {result['status']}.{duplicate_note}")]}


def order_tracking_node(state: State) -> dict:
    order_id = state.get("order_id", "").strip()
    if not order_id:
        return {"messages": [AIMessage(content="Provide an order ID so I can check its status.")]}

    result = get_order.invoke({"order_id": order_id})
    if not result.get("found", False):
        return {"messages": [AIMessage(content=f"I could not find an order with ID {order_id}.")]}

    return {"messages": [AIMessage(content=(
        f"Order {result['order_id']} is {result['status']} for product {result['product_id']} "
        f"with quantity {result['quantity']}."
    ))]}


def input_error_node(state: State) -> dict:
    message = state.get("error") or "I could not determine a supported AnyCart action."
    return {"messages": [AIMessage(content=message)]}


builder = StateGraph(State)
builder.add_node("orchestrator", orchestrator)
builder.add_node("recommendation_agent", recommendation_agent)
builder.add_node("order_management_node", order_management_node)
builder.add_node("order_tracking_node", order_tracking_node)
builder.add_node("input_error_node", input_error_node)
builder.add_edge(START, "orchestrator")
builder.add_conditional_edges("orchestrator", route_to_worker)
builder.add_edge("recommendation_agent", END)
builder.add_edge("order_management_node", END)
builder.add_edge("order_tracking_node", END)
builder.add_edge("input_error_node", END)

from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)


def run_request(message: str, *, thread_id: str, confirmed: bool = False, idempotency_key: str = ""):
    return graph.invoke(
        {
            "messages": [{"role": "user", "content": message}],
            "confirmed": confirmed,
            "idempotency_key": idempotency_key,
        },
        {"configurable": {"thread_id": thread_id}},
    )


if __name__ == "__main__":
    result = run_request("What kind of shoes do you have?", thread_id="anycart-demo")
    print(result["messages"][-1].text)
