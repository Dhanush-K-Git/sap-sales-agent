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
    close_sales_order,
    delete_sales_order,
    get_all_customers,
    get_customer
)

load_dotenv()


@tool
def tool_create_sales_order(card_code: str, doc_date: str,
                             doc_due_date: str, items: list) -> dict:
    """
    Create a new sales order in SAP B1.
    card_code: Customer code e.g C001
    doc_date: Order date e.g 2026-04-22
    doc_due_date: Due date e.g 2026-04-25
    items: List of items with item_code, quantity, unit_price
    """
    return create_sales_order(card_code, doc_date, doc_due_date, items)


@tool
def tool_get_sales_order(order_id: int) -> dict:
    """
    Get a specific sales order by its ID number.
    order_id: The order document number e.g 123
    """
    return get_sales_order(order_id)


@tool
def tool_get_all_sales_orders() -> dict:
    """
    Get all sales orders.
    """
    return get_all_sales_orders()


@tool
def tool_update_sales_order(order_id: int, comments: str) -> dict:
    """
    Update comments on an existing sales order.
    order_id: The order document number
    comments: New comment text to add
    """
    return update_sales_order(order_id, comments)


@tool
def tool_cancel_sales_order(order_id: int) -> dict:
    """
    Cancel an existing sales order.
    order_id: The order document number to cancel
    """
    return cancel_sales_order(order_id)


@tool
def tool_close_sales_order(order_id: int) -> dict:
    """
    Close an existing sales order.
    order_id: The order document number to close
    """
    return close_sales_order(order_id)


@tool
def tool_delete_sales_order(order_id: int) -> dict:
    """
    Delete an existing sales order.
    order_id: The order document number to delete
    """
    return delete_sales_order(order_id)

@tool
def tool_get_all_customers() -> dict:
    """
    Get all customers from the database.
    """
    return get_all_customers()


@tool
def tool_get_customer(card_code: str) -> dict:
    """
    Get a specific customer by card code.
    card_code: Customer code e.g C001
    """
    return get_customer(card_code)


# List of all tools
sales_order_tools = [
    tool_create_sales_order,
    tool_get_sales_order,
    tool_get_all_sales_orders,
    tool_update_sales_order,
    tool_cancel_sales_order,
    tool_close_sales_order,
    tool_delete_sales_order,
    tool_get_all_customers,
    tool_get_customer
]

# LLM brain
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# Create agent
sales_order_agent = create_react_agent(
    model=llm,
    tools=sales_order_tools,
    prompt="""You are a Sales Order Agent for SAP Business One.
    Your job is to help users manage sales orders.
    You can create, read, update, cancel, close and delete sales orders.
    
    IMPORTANT RULES:
    - Do NOT validate item codes - just use whatever ItemCode the user provides
    - Do NOT check if customers or items exist - just process the request
    - Always create the order with the exact details the user provides
    - If user gives CardCode, DocDate, DocDueDate and items - create it directly
    - Always be helpful and confirm actions clearly
    """
)


def run_sales_order_agent(user_message: str) -> str:
    """Run the sales order agent with a user message"""
    result = sales_order_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content