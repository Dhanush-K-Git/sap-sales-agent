from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv
from app.operations.utils import (
    create_sales_invoice,
    get_sales_invoice,
    get_all_sales_invoices,
    update_sales_invoice,
    cancel_sales_invoice,
    delete_sales_invoice
)

load_dotenv()


@tool
def tool_create_sales_invoice(card_code: str,
                               items: list) -> dict:
    """
    Create a new sales invoice.
    card_code: Customer code e.g C001
    items: List with ItemCode, Quantity, TaxCode, UnitPrice
    """
    return create_sales_invoice(card_code, items)


@tool
def tool_get_sales_invoice(invoice_id: int) -> dict:
    """
    Get a specific invoice by ID.
    invoice_id: Invoice ID number
    """
    return get_sales_invoice(invoice_id)


@tool
def tool_get_all_sales_invoices() -> dict:
    """Get all sales invoices."""
    return get_all_sales_invoices()


@tool
def tool_update_sales_invoice(invoice_id: int,
                               comments: str) -> dict:
    """
    Update invoice comments.
    invoice_id: Invoice ID number
    comments: New comment text
    """
    return update_sales_invoice(invoice_id, comments)


@tool
def tool_cancel_sales_invoice(invoice_id: int) -> dict:
    """
    Cancel a sales invoice.
    invoice_id: Invoice ID number
    """
    return cancel_sales_invoice(invoice_id)


@tool
def tool_delete_sales_invoice(invoice_id: int) -> dict:
    """
    Delete a sales invoice.
    invoice_id: Invoice ID number
    """
    return delete_sales_invoice(invoice_id)


sales_invoice_tools = [
    tool_create_sales_invoice,
    tool_get_sales_invoice,
    tool_get_all_sales_invoices,
    tool_update_sales_invoice,
    tool_cancel_sales_invoice,
    tool_delete_sales_invoice
]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

sales_invoice_agent = create_react_agent(
    model=llm,
    tools=sales_invoice_tools,
    prompt="""You are a Sales Invoice Agent for SAP B1.
    Your job is to manage sales invoices.
    You can create, read, update, cancel and delete invoices.
    Always confirm actions clearly.
    """
)


def run_sales_invoice_agent(user_message: str) -> str:
    result = sales_invoice_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content