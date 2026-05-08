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
def get_order_details(order_id: int) -> dict:
    """
    Get order details before updating.
    order_id: Order ID number
    """
    try:
        url = f"{BASE_URL}/Orders({order_id})"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@tool
def update_order_comments(order_id: int,
                           comments: str) -> dict:
    """
    Update order comments.
    order_id: Order ID number
    comments: New comment text
    """
    try:
        url = f"{BASE_URL}/Orders({order_id})"
        payload = {"Comments": comments}
        response = requests.patch(url, json=payload)
        return {
            "success": True,
            "message": f"Order {order_id} updated!"
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def update_order_status(order_id: int,
                         status: str) -> dict:
    """
    Update order status.
    order_id: Order ID number
    status: New status
    """
    try:
        url = f"{BASE_URL}/Orders({order_id})"
        payload = {"Status": status}
        response = requests.patch(url, json=payload)
        return {
            "success": True,
            "message": f"Order {order_id} status updated!"
        }
    except Exception as e:
        return {"error": str(e)}


update_tools = [
    get_order_details,
    update_order_comments,
    update_order_status
]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

update_agent = create_react_agent(
    model=llm,
    tools=update_tools,
    prompt="""You are an Update Agent for SAP B1.
    Your job is to update existing sales orders.

    WORKFLOW:
    1. Get order details first
    2. Make the requested update
    3. Confirm what was updated
    """
)


def run_update_agent(user_message: str) -> str:
    result = update_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content