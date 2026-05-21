from app.operations.llm_config import llm_validate as llm
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv
from app.operations.utils import execute_query

load_dotenv()


@tool
def validate_customer(card_code: str) -> dict:
    """
    Validate if customer exists in SAP B1.
    card_code: Customer code e.g. C001
    """
    # Hit the SAP BusinessPartners endpoint instead of writing SQL
    result = sap_get(f"BusinessPartners('{card_code}')")
    
    if result.get("success"):
        # If SAP returns data, the customer is valid
        return {
            "valid": True,
            "card_name": result["data"].get("CardName"),
            "credit_limit": result["data"].get("CreditLimit")
        }
    else:
        return {"valid": False, "error": "Customer not found in SAP"}


@tool
def validate_credit(card_code: str,
                     order_total: float) -> dict:
    """
    Validate customer credit limit.
    card_code: Customer code
    order_total: Total order amount
    """
    sql = f"""
        SELECT "CardName", "CreditLimit", "Balance"
        FROM "OCRD"
        WHERE "CardCode" = '{card_code}'
    """
    data = execute_query(sql)
    if data.get("data") and len(data["data"]) > 0:
        customer = data["data"][0]
        credit_limit = float(customer["creditlimit"])
        balance = float(customer["balance"])
        available = credit_limit - balance

        if available >= order_total:
            return {
                "valid": True,
                "available_credit": available,
                "message": f"Credit OK! Available: ₹{available}"
            }
        return {
            "valid": False,
            "available_credit": available,
            "message": f"⚠️ Credit limit exceeded! Available: ₹{available}, Required: ₹{order_total}"
        }
    return {"valid": False, "message": "Customer not found!"}


@tool
def validate_stock(item_code: str = None,
                    item_name: str = None,
                    quantity: float = 1) -> dict:
    """
    Validate item stock availability.
    item_code: Item code e.g I001 (optional)
    item_name: Item name e.g Laptop (optional)
    quantity: Required quantity
    """
    if item_name:
        sql = f"""
            SELECT "ItemCode", "ItemName", "Stock", "Price"
            FROM "OITM"
            WHERE "ItemName" ILIKE '%{item_name}%'
        """
    else:
        sql = f"""
            SELECT "ItemCode", "ItemName", "Stock", "Price"
            FROM "OITM"
            WHERE "ItemCode" = '{item_code}'
        """

    data = execute_query(sql)
    if data.get("data") and len(data["data"]) > 0:
        item = data["data"][0]
        stock = float(item["stock"])

        if stock >= quantity:
            return {
                "valid": True,
                "item_name": item["itemname"],
                "available_stock": stock,
                "message": f"Stock OK! {item['itemname']} has {stock} units!"
            }
        return {
            "valid": False,
            "item_name": item["itemname"],
            "available_stock": stock,
            "message": f"⚠️ Low stock! {item['itemname']} has only {stock} units, Required: {quantity}"
        }
    return {"valid": False, "message": "Item not found!"}


validation_tools = [
    validate_customer,
    validate_credit,
    validate_stock
]

validation_agent = create_react_agent(
    model=llm,
    tools=validation_tools,
    prompt="""You are a Validation Agent for SAP B1.
    You validate orders before creation.

    Tools:
    1. validate_customer - Check if customer exists
    2. validate_credit - Check credit limit
    3. validate_stock - Check item stock

    Always run validations and explain results clearly.
    If validation fails, warn the user but allow proceeding.
    """
)


def run_validation_agent(card_code: str,
                          order_total: float,
                          items: list) -> dict:
    message = f"""
    Validate this order:
    Customer: {card_code}
    Total: {order_total}
    Items: {items}
    """
    result = validation_agent.invoke({
        "messages": [HumanMessage(content=message)]
    })
    return {
        "response": result["messages"][-1].content,
        "proceed": True
    }