from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv
from tools.sap_tools import (
    create_sales_invoice,
    get_sales_invoice,
    get_all_sales_invoices,
    update_sales_invoice,
    cancel_sales_invoice,
    delete_sales_invoice
)

load_dotenv()


@tool
def tool_create_sales_invoice(card_code: str, items: list) -> dict:
    """
    Create a new sales invoice.
    card_code: Customer code e.g C001
    items: List of items with item_code, quantity, tax_code, unit_price
    """
    return create_sales_invoice(card_code, items)


@tool
def tool_get_sales_invoice(invoice_id: int) -> dict:
    """
    Get a specific sales invoice by its ID number.
    invoice_id: The invoice document number e.g 123
    """
    return get_sales_invoice(invoice_id)


@tool
def tool_get_all_sales_invoices() -> dict:
    """
    Get all sales invoices.
    """
    return get_all_sales_invoices()


@tool
def tool_update_sales_invoice(invoice_id: int, comments: str) -> dict:
    """
    Update comments on an existing sales invoice.
    invoice_id: The invoice document number
    comments: New comment text to add
    """
    return update_sales_invoice(invoice_id, comments)


@tool
def tool_cancel_sales_invoice(invoice_id: int) -> dict:
    """
    Cancel an existing sales invoice.
    invoice_id: The invoice document number to cancel
    """
    return cancel_sales_invoice(invoice_id)


@tool
def tool_delete_sales_invoice(invoice_id: int) -> dict:
    """
    Delete an existing sales invoice.
    invoice_id: The invoice document number to delete
    """
    return delete_sales_invoice(invoice_id)


# List of all tools
sales_invoice_tools = [
    tool_create_sales_invoice,
    tool_get_sales_invoice,
    tool_get_all_sales_invoices,
    tool_update_sales_invoice,
    tool_cancel_sales_invoice,
    tool_delete_sales_invoice
]

# LLM brain
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# Create agent
sales_invoice_agent = create_react_agent(
    model=llm,
    tools=sales_invoice_tools,
    prompt="""You are a Sales Invoice Agent for SAP Business One.
    Your job is to help users manage sales invoices.
    You can create, read, update, cancel and delete sales invoices.
    
    IMPORTANT RULES:
    - Do NOT validate item codes - just use whatever ItemCode the user provides
    - Do NOT check if customers or items exist - just process the request
    - Always create the invoice with the exact details the user provides
    - Always be helpful and confirm actions clearly
    """
)


def run_sales_invoice_agent(user_message: str) -> str:
    """Run the sales invoice agent with a user message"""
    result = sales_invoice_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content