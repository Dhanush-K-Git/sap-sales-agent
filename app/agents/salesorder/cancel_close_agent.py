from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
import requests
from dotenv import load_dotenv
from app.operations.utils import BASE_URL

load_dotenv()


@tool
def get_order_status(order_id: int) -> dict:
    """
    Get current order status.
    order_id: Order ID number
    """
    try:
        url = f"{BASE_URL}/Orders({order_id})"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@tool
def cancel_order(order_id: int) -> dict:
    """
    Cancel a sales order.
    order_id: Order ID number
    """
    try:
        url = f"{BASE_URL}/Orders({order_id})/Cancel"
        response = requests.post(url)
        return {
            "success": True,
            "message": f"Order {order_id} cancelled!"
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def close_order(order_id: int) -> dict:
    """
    Close a completed sales order.
    order_id: Order ID number
    """
    try:
        url = f"{BASE_URL}/Orders({order_id})/Close"
        response = requests.post(url)
        return {
            "success": True,
            "message": f"Order {order_id} closed!"
        }
    except Exception as e:
        return {"error": str(e)}


cancel_close_tools = [
    get_order_status,
    cancel_order,
    close_order
]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

cancel_close_agent = create_react_agent(
    model=llm,
    tools=cancel_close_tools,
    prompt="""You are a Cancel/Close Agent for SAP B1.
    Your job is to cancel or close sales orders.

    WORKFLOW:
    1. Get order status first
    2. Cancel or Close as requested
    3. Confirm the action
    """
)


def run_cancel_close_agent(user_message: str) -> str:
    result = cancel_close_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content