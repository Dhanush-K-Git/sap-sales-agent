from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://sap-sales-agent-1.onrender.com"


# ─────────────────────────────────────────────
# 🔧 CANCEL/CLOSE TOOLS
# ─────────────────────────────────────────────

@tool
def cancel_order(order_id: int) -> dict:
    """
    Cancel a sales order.
    order_id: The order ID number to cancel
    """
    try:
        url = f"{BASE_URL}/Orders({order_id})/Cancel"
        response = requests.post(url)
        return {
            "success": True,
            "message": f"Order {order_id} cancelled successfully!"
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def close_order(order_id: int) -> dict:
    """
    Close a completed sales order.
    order_id: The order ID number to close
    """
    try:
        url = f"{BASE_URL}/Orders({order_id})/Close"
        response = requests.post(url)
        return {
            "success": True,
            "message": f"Order {order_id} closed successfully!"
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_order_status(order_id: int) -> dict:
    """
    Get current status of an order.
    order_id: The order ID number
    """
    try:
        url = f"{BASE_URL}/Orders({order_id})"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 🤖 BUILD CANCEL/CLOSE AGENT
# ─────────────────────────────────────────────

cancel_close_tools = [
    cancel_order,
    close_order,
    get_order_status
]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

cancel_close_agent = create_react_agent(
    model=llm,
    tools=cancel_close_tools,
    prompt="""You are a Cancel/Close Agent for SAP Business One.
    Your job is to cancel or close sales orders.

    You can:
    1. get_order_status → Check current order status
    2. cancel_order → Cancel an order
    3. close_order → Close a completed order

    WORKFLOW:
    1. Get order status first
    2. Check if action is valid
    3. Cancel or Close as requested
    4. Confirm the action

    IMPORTANT RULES:
    - Always check order status before action
    - Cancelled orders cannot be closed
    - Always confirm after action
    - Be clear about what happened
    """
)


def run_cancel_close_agent(user_message: str) -> str:
    """Run the cancel/close agent"""
    result = cancel_close_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content