from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from app.operations.llm_config import llm_cancel as llm
from app.operations.sap_client import (
    cancel_sales_order, close_sales_order
)
from app.operations.utils import execute_query


@tool
def get_order_details(doc_num: int) -> dict:
    """Get order status before cancel/close. doc_num: Order number"""
    sql = f"""
        SELECT "DocNum", "DocEntry", "CardName",
               "DocTotal", "DocStatus"
        FROM "ORDR" WHERE "DocNum" = {doc_num}
    """
    return execute_query(sql)


@tool
def tool_cancel_order(doc_entry: int) -> dict:
    """Cancel a sales order. doc_entry: DocEntry from order details"""
    return cancel_sales_order(doc_entry)


@tool
def tool_close_order(doc_entry: int) -> dict:
    """Close a completed sales order. doc_entry: DocEntry from order details"""
    return close_sales_order(doc_entry)


cancel_tools = [get_order_details, tool_cancel_order, tool_close_order]

cancel_agent = create_react_agent(
    model=llm,
    tools=cancel_tools,
    prompt="""You are a SAP B1 Cancel/Close specialist at Techative Pvt Ltd.

WORKFLOW:
1. get_order_details  → check current status, get DocEntry
2. If already closed  → tell user, stop
3. tool_cancel_order or tool_close_order → use DocEntry
4. Confirm the action

Cancel = order will NOT be fulfilled.
Close  = order is completed/delivered."""
)


def run_cancel_close_agent(user_message: str) -> str:
    result = cancel_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content