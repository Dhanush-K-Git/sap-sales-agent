from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://sap-sales-agent-1.onrender.com"

# ─────────────────────────────────────────────
# 🔧 VALIDATION TOOLS
# ─────────────────────────────────────────────

@tool
def validate_customer(card_code: str) -> dict:
    """
    Validate if customer exists in database.
    card_code: Customer code e.g C001
    """
    try:
        sql = f"""
            SELECT 
                "CardCode",
                "CardName",
                "CreditLimit",
                "Balance"
            FROM "OCRD"
            WHERE "CardCode" = '{card_code}'
        """
        response = requests.get(
            f"{BASE_URL}/query",
            params={"sql": sql}
        )
        data = response.json()
        if data.get("data") and len(data["data"]) > 0:
            customer = data["data"][0]
            return {
                "valid": True,
                "customer": customer,
                "message": f"Customer {customer['cardname']} exists!"
            }
        return {
            "valid": False,
            "message": f"Customer {card_code} not found!"
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def validate_credit(card_code: str, 
                     order_total: float) -> dict:
    """
    Validate if customer has enough credit limit.
    card_code: Customer code e.g C001
    order_total: Total amount of the order
    """
    try:
        sql = f"""
            SELECT 
                "CardName",
                "CreditLimit",
                "Balance"
            FROM "OCRD"
            WHERE "CardCode" = '{card_code}'
        """
        response = requests.get(
            f"{BASE_URL}/query",
            params={"sql": sql}
        )
        data = response.json()
        if data.get("data") and len(data["data"]) > 0:
            customer = data["data"][0]
            credit_limit = float(customer["creditlimit"])
            balance = float(customer["balance"])
            available_credit = credit_limit - balance

            if available_credit >= order_total:
                return {
                    "valid": True,
                    "available_credit": available_credit,
                    "order_total": order_total,
                    "message": f"Credit OK! Available: ₹{available_credit}"
                }
            else:
                return {
                    "valid": False,
                    "available_credit": available_credit,
                    "order_total": order_total,
                    "message": f"⚠️ Warning: Credit limit exceeded! Available: ₹{available_credit}, Order Total: ₹{order_total}. Proceeding anyway!"
                }
        return {
            "valid": False,
            "message": f"Customer {card_code} not found!"
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def validate_stock(item_code: str, 
                    quantity: float) -> dict:
    """
    Validate if item has enough stock.
    item_code: Item code e.g I001
    quantity: Required quantity
    """
    try:
        sql = f"""
            SELECT 
                "ItemCode",
                "ItemName",
                "Stock",
                "Price"
            FROM "OITM"
            WHERE "ItemCode" = '{item_code}'
        """
        response = requests.get(
            f"{BASE_URL}/query",
            params={"sql": sql}
        )
        data = response.json()
        if data.get("data") and len(data["data"]) > 0:
            item = data["data"][0]
            stock = float(item["stock"])

            if stock >= quantity:
                return {
                    "valid": True,
                    "available_stock": stock,
                    "required_quantity": quantity,
                    "message": f"Stock OK! Available: {stock} units"
                }
            else:
                return {
                    "valid": False,
                    "available_stock": stock,
                    "required_quantity": quantity,
                    "message": f"⚠️ Warning: Insufficient stock! Available: {stock}, Required: {quantity}. Proceeding anyway!"
                }
        return {
            "valid": False,
            "message": f"Item {item_code} not found!"
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def validate_order(card_code: str,
                    order_total: float,
                    items: list) -> dict:
    """
    Run all validations for an order at once.
    card_code: Customer code
    order_total: Total order amount
    items: List of items with item_code and quantity
    """
    try:
        results = {
            "customer_validation": None,
            "credit_validation": None,
            "stock_validations": [],
            "overall_valid": True,
            "warnings": []
        }

        # Validate customer
        customer_result = validate_customer.invoke(
            {"card_code": card_code}
        )
        results["customer_validation"] = customer_result
        if not customer_result.get("valid"):
            results["overall_valid"] = False
            results["warnings"].append(
                customer_result.get("message")
            )

        # Validate credit
        credit_result = validate_credit.invoke({
            "card_code": card_code,
            "order_total": order_total
        })
        results["credit_validation"] = credit_result
        if not credit_result.get("valid"):
            results["warnings"].append(
                credit_result.get("message")
            )

        # Validate stock for each item
        for item in items:
            stock_result = validate_stock.invoke({
                "item_code": item.get("item_code") or item.get("ItemCode"),
                "quantity": item.get("quantity") or item.get("Quantity")
            })
            results["stock_validations"].append(stock_result)
            if not stock_result.get("valid"):
                results["warnings"].append(
                    stock_result.get("message")
                )

        return results

    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 🤖 BUILD VALIDATION AGENT
# ─────────────────────────────────────────────

validation_tools = [
    validate_customer,
    validate_credit,
    validate_stock,
    validate_order
]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

validation_agent = create_react_agent(
    model=llm,
    tools=validation_tools,
    prompt="""You are a Validation Agent for SAP Business One.
    You validate orders before they are created.

    You can:
    1. validate_customer → Check if customer exists
    2. validate_credit → Check credit limit
    3. validate_stock → Check item stock
    4. validate_order → Run ALL validations at once

    IMPORTANT RULES:
    - Always run all validations
    - If validation fails → WARN the user
    - Never block order creation
    - Always explain results clearly
    - Show warnings in a friendly way
    """
)


def run_validation_agent(card_code: str,
                          order_total: float,
                          items: list) -> dict:
    """Run validation for an order"""
    message = f"""
    Validate this order:
    Customer: {card_code}
    Total: {order_total}
    Items: {items}
    
    Run validate_order with these details.
    """
    result = validation_agent.invoke({
        "messages": [HumanMessage(content=message)]
    })
    return {
        "response": result["messages"][-1].content,
        "proceed": True
    }