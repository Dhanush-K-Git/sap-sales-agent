from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
import requests
from dotenv import load_dotenv
from app.operations.utils import execute_query, BASE_URL

load_dotenv()


@tool
def create_order_with_validation(
        card_code: str,
        doc_date: str,
        doc_due_date: str,
        items: list,
        order_total: float) -> dict:
    """
    Create a sales order with validation.
    card_code: Customer code e.g C001
    doc_date: Order date e.g 2026-04-28
    doc_due_date: Due date e.g 2026-04-30
    items: List with ItemCode, Quantity, UnitPrice
    order_total: Total order amount
    """
    warnings = []

    # Validate Customer
    customer_data = execute_query(f"""
        SELECT "CardCode", "CardName",
               "CreditLimit", "Balance"
        FROM "OCRD"
        WHERE "CardCode" = '{card_code}'
    """)

    if not customer_data.get("data") or \
       len(customer_data["data"]) == 0:
        warnings.append(
            f"⚠️ Customer {card_code} not found!"
        )
    else:
        customer = customer_data["data"][0]
        credit_limit = float(customer["creditlimit"])
        balance = float(customer["balance"])
        available = credit_limit - balance
        if available < order_total:
            warnings.append(
                f"⚠️ Credit limit exceeded! "
                f"Available: ₹{available}, "
                f"Order Total: ₹{order_total}"
            )

    # Validate Stock
    for item in items:
        item_code = item.get("ItemCode") or \
                    item.get("item_code")
        quantity = item.get("Quantity") or \
                   item.get("quantity")

        stock_data = execute_query(f"""
            SELECT "ItemCode", "ItemName", "Stock"
            FROM "OITM"
            WHERE "ItemCode" = '{item_code}'
        """)

        if stock_data.get("data") and \
           len(stock_data["data"]) > 0:
            item_info = stock_data["data"][0]
            stock = float(item_info["stock"])
            if stock < float(quantity):
                warnings.append(
                    f"⚠️ Low stock for "
                    f"{item_info['itemname']}! "
                    f"Available: {stock}, "
                    f"Required: {quantity}"
                )

    # Create Order
    try:
        url = f"{BASE_URL}/Orders"
        payload = {
            "CardCode": card_code,
            "DocDate": doc_date,
            "DocDueDate": doc_due_date,
            "DocumentLines": [
                {
                    "ItemCode": item.get("ItemCode") or
                                item.get("item_code"),
                    "Quantity": item.get("Quantity") or
                                item.get("quantity"),
                    "UnitPrice": item.get("UnitPrice") or
                                 item.get("unit_price")
                }
                for item in items
            ]
        }
        response = requests.post(url, json=payload)
        order_data = response.json()

        return {
            "success": True,
            "order": order_data,
            "warnings": warnings
        }
    except Exception as e:
        return {"error": str(e)}


create_tools = [create_order_with_validation]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

create_agent = create_react_agent(
    model=llm,
    tools=create_tools,
    prompt="""You are a Create Agent for SAP B1.
    Your job is to create sales orders.

    WORKFLOW:
    1. Extract all order details from message
    2. Calculate order total (qty × price)
    3. Call create_order_with_validation
    4. Show any warnings to user
    5. Confirm order creation

    Always show validation warnings if any!
    """
)


def run_create_agent(user_message: str) -> str:
    result = create_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content