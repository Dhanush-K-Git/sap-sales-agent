from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from app.operations.llm_config import llm_return as llm
from app.operations.sap_client import (
    create_sales_return, cancel_sales_return,
    close_sales_return, reopen_sales_return
)
from app.operations.utils import execute_query


@tool
def tool_create_return(card_code: str, item_codes: list,
                       quantities: list, unit_prices: list,
                       tax_codes: list = None) -> dict:
    """
    Create a sales return via SAP B1.
    card_code: Customer code e.g C001
    item_codes: List e.g ['I001']
    quantities: List e.g [100]
    unit_prices: List e.g [50.0]
    tax_codes: List e.g ['T1'] (optional)
    """
    if not tax_codes:
        tax_codes = ["T1"] * len(item_codes)
    items = [
        {"ItemCode": ic, "Quantity": q,
         "UnitPrice": p, "TaxCode": tc}
        for ic, q, p, tc in zip(item_codes, quantities,
                                 unit_prices, tax_codes)
    ]
    return create_sales_return(card_code, items)


@tool
def tool_cancel_return(doc_entry: int) -> dict:
    """Cancel a sales return. doc_entry: Return DocEntry"""
    return cancel_sales_return(doc_entry)


@tool
def tool_close_return(doc_entry: int) -> dict:
    """Close a sales return. doc_entry: Return DocEntry"""
    return close_sales_return(doc_entry)


@tool
def tool_reopen_return(doc_entry: int) -> dict:
    """Reopen a sales return. doc_entry: Return DocEntry"""
    return reopen_sales_return(doc_entry)


@tool
def get_all_returns() -> dict:
    """Get all sales returns from database."""
    sql = """
        SELECT "DocNum", "DocDate", "CardName",
               "DocTotal", "DocStatus"
        FROM "ORDN"
        ORDER BY "DocNum" DESC
    """
    return execute_query(sql)


return_tools = [
    tool_create_return, tool_cancel_return,
    tool_close_return, tool_reopen_return,
    get_all_returns
]

return_agent = create_react_agent(
    model=llm,
    tools=return_tools,
    prompt="""You are a SAP B1 Sales Return specialist at Techative Pvt Ltd.

OPERATIONS:
- Create return → tool_create_return
- Cancel return → tool_cancel_return
- Close return  → tool_close_return
- Reopen return → tool_reopen_return
- List returns  → get_all_returns

Always confirm DocEntry after creation.
Default TaxCode is T1 if not specified."""
)


def run_sales_return_agent(user_message: str) -> str:
    result = return_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content