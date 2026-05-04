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
# 🔧 UPDATE TOOLS
# ─────────────────────────────────────────────

@tool
def update_order_comments(order_id: int,
                           comments: str) -> dict:
    """
    Update comments on a sales order.
    order_id: The order ID number
    comments: New comment to add
    """
    try:
        url = f"{BASE_URL}/Orders({order_id})"
        payload = {"Comments": comments}
        response = requests.patch(url, json=payload)
        return {
            "success": True,
            "message": f"Order {order_id} comments updated!"
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def update_order_status(order_id: int,
                         status: str) -> dict:
    """
    Update status of a sales order.
    order_id: The order ID number
    status: New status - 'open' or 'closed'
    """
    try:
        url = f"{BASE_URL}/Orders({order_id})"
        payload = {"Status": status}
        response = requests.patch(url, json=payload)
        return {
            "success": True,
            "message": f"Order {order_id} status updated to {status}!"
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_order_details(order_id: int) -> dict:
    """
    Get details of a specific order before updating.
    order_id: The order ID number
    """
    try:
        url = f"{BASE_URL}/Orders({order_id})"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 🤖 BUILD UPDATE AGENT
# ─────────────────────────────────────────────

update_tools = [
    update_order_comments,
    update_order_status,
    get_order_details
]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

update_agent = create_react_agent(
    model=llm,
    tools=update_tools,
    prompt="""You are an Update Agent for SAP Business One.
    Your job is to update existing sales orders.

    You can:
    1. get_order_details → See current order details
    2. update_order_comments → Update comments
    3. update_order_status → Update status

    WORKFLOW:
    1. Get current order details first
    2. Make the requested update
    3. Confirm what was updated

    IMPORTANT RULES:
    - Always get order details before updating
    - Always confirm after updating
    - Be clear about what changed
    """
)


def run_update_agent(user_message: str) -> str:
    """Run the update agent"""
    result = update_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content