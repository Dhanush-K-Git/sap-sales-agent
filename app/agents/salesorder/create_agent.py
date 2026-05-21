from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from app.operations.llm_config import llm_create as llm
from app.operations.sap_client import create_sales_order
from app.operations.utils import execute_query
from datetime import date, timedelta


@tool
def validate_customer(card_code: str) -> dict:
    """Check if customer exists. card_code: e.g C001"""
    sql = f"""
        SELECT "CardCode", "CardName", "CreditLimit", "Balance"
        FROM "OCRD" WHERE "CardCode" = '{card_code}'
    """
    return execute_query(sql)


@tool
def validate_item(item_code: str) -> dict:
    """Check item exists and get price. item_code: e.g I001"""
    sql = f"""
        SELECT "ItemCode", "ItemName", "Price", "Stock"
        FROM "OITM" WHERE "ItemCode" = '{item_code}'
    """
    return execute_query(sql)


@tool
def tool_create_order(card_code: str, item_codes: list,
                      quantities: list, unit_prices: list) -> dict:
    """
    Create sales order via SAP B1 API.
    card_code: Customer code e.g C001
    item_codes: List e.g ['I001', 'I002']
    quantities: List e.g [2, 1]
    unit_prices: List e.g [100.0, 50.0]
    """
    today      = str(date.today())
    due_date   = str(date.today() + timedelta(days=3))
    items = [
        {"ItemCode": ic, "Quantity": q, "UnitPrice": p}
        for ic, q, p in zip(item_codes, quantities, unit_prices)
    ]
    return create_sales_order(card_code, today, due_date, items)


create_tools = [validate_customer, validate_item, tool_create_order]

create_agent = create_react_agent(
    model=llm,
    tools=create_tools,
    prompt="""You are a SAP B1 Sales Order Creation specialist at Techative Pvt Ltd.

STRICT WORKFLOW — follow this every time:
1. validate_customer  → confirm customer exists
2. validate_item      → confirm each item exists, note the price
3. tool_create_order  → create only after both validations pass

KNOWN CUSTOMERS : C001 to C010
KNOWN ITEMS     : I001(Laptop), I002(Mouse), I003(Keyboard),
                  I004(Monitor), I005(Headphones)

RULES:
- If validation fails → tell the user clearly, do not create
- Use the UnitPrice from validate_item (item master price)
- After creating → confirm DocNum, customer, items, total
- Always be friendly and professional"""
)


def run_create_agent(user_message: str) -> str:
    result = create_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content