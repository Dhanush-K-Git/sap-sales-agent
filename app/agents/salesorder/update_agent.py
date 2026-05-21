from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from app.operations.llm_config import llm_update as llm
from app.operations.sap_client import update_sales_order
from app.operations.utils import execute_query


@tool
def get_order_details(doc_num: int) -> dict:
    """Get order details before updating. doc_num: Order number e.g 1001"""
    sql = f"""
        SELECT o."DocNum", o."DocEntry", o."CardName",
               o."DocTotal", o."DocStatus", o."Comments",
               l."ItemName", l."Quantity", l."Price"
        FROM "ORDR" o
        JOIN "RDR1" l ON o."DocEntry" = l."DocEntry"
        WHERE o."DocNum" = {doc_num}
    """
    return execute_query(sql)


@tool
def tool_update_order(doc_entry: int, comments: str) -> dict:
    """
    Update a sales order comment via SAP B1 API.
    doc_entry: DocEntry number (from order details)
    comments: New comment text
    """
    return update_sales_order(doc_entry, comments)


update_tools = [get_order_details, tool_update_order]

update_agent = create_react_agent(
    model=llm,
    tools=update_tools,
    prompt="""You are a SAP B1 Sales Order Update specialist at Techative Pvt Ltd.

WORKFLOW:
1. get_order_details → always fetch order first, get DocEntry
2. Show user what the current order looks like
3. tool_update_order → apply the update using DocEntry
4. Confirm what was changed"""
)


def run_update_agent(user_message: str) -> str:
    result = update_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content