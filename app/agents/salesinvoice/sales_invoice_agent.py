from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from app.operations.llm_config import llm_invoice as llm
from app.operations.sap_client import (
    create_sales_invoice, cancel_sales_invoice,
    close_sales_invoice, reopen_sales_invoice
)
from app.operations.utils import execute_query


@tool
def tool_create_invoice(card_code: str, item_codes: list,
                        quantities: list, unit_prices: list,
                        tax_codes: list = None) -> dict:
    """
    Create a sales invoice via SAP B1.
    card_code: Customer code e.g C001
    item_codes: List e.g ['I001']
    quantities: List e.g [100]
    unit_prices: List e.g [30.0]
    tax_codes: List e.g ['T1'] (optional, defaults to T1)
    """
    if not tax_codes:
        tax_codes = ["T1"] * len(item_codes)
    items = [
        {"ItemCode": ic, "Quantity": q,
         "UnitPrice": p, "TaxCode": tc}
        for ic, q, p, tc in zip(item_codes, quantities,
                                 unit_prices, tax_codes)
    ]
    return create_sales_invoice(card_code, items)


@tool
def tool_cancel_invoice(doc_entry: int) -> dict:
    """Cancel a sales invoice. doc_entry: Invoice DocEntry"""
    return cancel_sales_invoice(doc_entry)


@tool
def tool_close_invoice(doc_entry: int) -> dict:
    """Close a sales invoice. doc_entry: Invoice DocEntry"""
    return close_sales_invoice(doc_entry)


@tool
def tool_reopen_invoice(doc_entry: int) -> dict:
    """Reopen a closed invoice. doc_entry: Invoice DocEntry"""
    return reopen_sales_invoice(doc_entry)


@tool
def get_all_invoices() -> dict:
    """Get all sales invoices from database."""
    sql = """
        SELECT "DocNum", "DocDate", "CardName",
               "DocTotal", "DocStatus"
        FROM "OINV"
        ORDER BY "DocNum" DESC
    """
    return execute_query(sql)


invoice_tools = [
    tool_create_invoice, tool_cancel_invoice,
    tool_close_invoice, tool_reopen_invoice,
    get_all_invoices
]

invoice_agent = create_react_agent(
    model=llm,
    tools=invoice_tools,
    prompt="""You are a SAP B1 Sales Invoice specialist at Techative Pvt Ltd.

OPERATIONS:
- Create invoice  → tool_create_invoice
- Cancel invoice  → tool_cancel_invoice
- Close invoice   → tool_close_invoice
- Reopen invoice  → tool_reopen_invoice
- List invoices   → get_all_invoices

Always confirm DocEntry after creation.
Default TaxCode is T1 if not specified."""
)


def run_sales_invoice_agent(user_message: str) -> str:
    result = invoice_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content