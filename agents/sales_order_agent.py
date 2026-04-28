from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv
from tools.sap_tools import (
    create_sales_order,
    get_sales_order,
    get_all_sales_orders,
    update_sales_order,
    cancel_sales_order,
    close_sales_order
)

load_dotenv()

# ─────────────────────────────────────────────
# 🔧 WRAP SAP FUNCTIONS AS TOOLS
# The agent can only use functions that are 
# wrapped with @tool decorator
# ─────────────────────────────────────────────

@tool
def tool_create_sales_order(card_code: str, doc_date: str,
                             doc_due_date: str, items: list) -> dict:
    """
    Create a new sales order in SAP B1.
    card_code: Customer code e.g C001
    doc_date: Order date e.g 2026-04-22
    doc_due_date: Due date e.g 2026-04-25
    items: List of items with ItemCode, Quantity, UnitPrice
    """
    cookies = None  # Will be passed from session
    return create_sales_order(card_code, doc_date, 
                               doc_due_date, items, cookies)


@tool
def tool_get_sales_order(order_id: int) -> dict:
    """
    Get a specific sales order by its ID number.
    order_id: The SAP order document number e.g 123
    """
    cookies = None
    return get_sales_order(order_id, cookies)


@tool
def tool_get_all_sales_orders() -> dict:
    """
    Get all sales orders from SAP B1.
    """
    cookies = None
    return get_all_sales_orders(cookies)


@tool
def tool_update_sales_order(order_id: int, comments: str) -> dict:
    """
    Update comments on an existing sales order.
    order_id: The SAP order document number
    comments: New comment text to add
    """
    cookies = None
    return update_sales_order(order_id, comments, cookies)


@tool
def tool_cancel_sales_order(order_id: int) -> dict:
    """
    Cancel an existing sales order.
    order_id: The SAP order document number to cancel
    """
    cookies = None
    return cancel_sales_order(order_id, cookies)


@tool
def tool_close_sales_order(order_id: int) -> dict:
    """
    Close an existing sales order.
    order_id: The SAP order document number to close
    """
    cookies = None
    return close_sales_order(order_id, cookies)


# ─────────────────────────────────────────────
# 🤖 BUILD THE SALES ORDER AGENT
# ─────────────────────────────────────────────

# List of all tools this agent can use
sales_order_tools = [
    tool_create_sales_order,
    tool_get_sales_order,
    tool_get_all_sales_orders,
    tool_update_sales_order,
    tool_cancel_sales_order,
    tool_close_sales_order
]

# The LLM brain of the agent
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# Create the agent
sales_order_agent = create_react_agent(
    model=llm,
    tools=sales_order_tools,
    prompt="""You are a Sales Order Agent for SAP Business One.
    Your job is to help users manage sales orders.
    You can create, read, update, cancel and close sales orders.
    Always be helpful and confirm actions clearly.
    If you need information to complete a task, ask the user for it.
    """
)


def run_sales_order_agent(user_message: str) -> str:
    """Run the sales order agent with a user message"""
    result = sales_order_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content