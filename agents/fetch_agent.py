from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# 🌍 RENDER URL
# ─────────────────────────────────────────────
BASE_URL = "https://sap-sales-agent-1.onrender.com"

# ─────────────────────────────────────────────
# 📊 SEMANTIC SCHEMA
# ─────────────────────────────────────────────
SEMANTIC_SCHEMA = {
    "sales_order": {
        "header_table": "ORDR",
        "line_table": "RDR1",
        "join": '"ORDR"."DocEntry" = "RDR1"."DocEntry"',
        "fields": {
            "order_number": '"ORDR"."DocNum"',
            "date": '"ORDR"."DocDate"',
            "due_date": '"ORDR"."DocDueDate"',
            "customer_code": '"ORDR"."CardCode"',
            "customer_name": '"ORDR"."CardName"',
            "total": '"ORDR"."DocTotal"',
            "status": '"ORDR"."DocStatus"',
            "comments": '"ORDR"."Comments"',
            "item_code": '"RDR1"."ItemCode"',
            "item_name": '"RDR1"."ItemName"',
            "quantity": '"RDR1"."Quantity"',
            "price": '"RDR1"."Price"',
            "line_total": '"RDR1"."LineTotal"'
        }
    }
}


# ─────────────────────────────────────────────
# 🔧 TOOLS
# ─────────────────────────────────────────────

@tool
def get_all_orders() -> dict:
    """
    Get all sales orders from database.
    Use when user asks to see all orders.
    """
    try:
        sql = """
            SELECT 
                "ORDR"."DocNum" as order_number,
                "ORDR"."DocDate" as date,
                "ORDR"."CardName" as customer_name,
                "ORDR"."DocTotal" as total,
                "ORDR"."DocStatus" as status,
                "RDR1"."ItemName" as item_name,
                "RDR1"."Quantity" as quantity,
                "RDR1"."Price" as price
            FROM "ORDR"
            JOIN "RDR1" ON "ORDR"."DocEntry" = "RDR1"."DocEntry"
            ORDER BY "ORDR"."DocNum"
        """
        response = requests.get(
            f"{BASE_URL}/query",
            params={"sql": sql}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@tool
def get_orders_by_customer(customer_name: str) -> dict:
    """
    Get all sales orders for a specific customer.
    customer_name: Name of the customer to search
    """
    try:
        sql = f"""
            SELECT 
                "ORDR"."DocNum" as order_number,
                "ORDR"."DocDate" as date,
                "ORDR"."CardName" as customer_name,
                "ORDR"."DocTotal" as total,
                "ORDR"."DocStatus" as status,
                "RDR1"."ItemName" as item_name,
                "RDR1"."Quantity" as quantity,
                "RDR1"."Price" as price
            FROM "ORDR"
            JOIN "RDR1" ON "ORDR"."DocEntry" = "RDR1"."DocEntry"
            WHERE "ORDR"."CardName" ILIKE '%{customer_name}%'
            ORDER BY "ORDR"."DocNum"
        """
        response = requests.get(
            f"{BASE_URL}/query",
            params={"sql": sql}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@tool
def get_open_orders() -> dict:
    """
    Get all open sales orders.
    Use when user asks for open or pending orders.
    """
    try:
        sql = """
            SELECT 
                "ORDR"."DocNum" as order_number,
                "ORDR"."DocDate" as date,
                "ORDR"."CardName" as customer_name,
                "ORDR"."DocTotal" as total,
                "RDR1"."ItemName" as item_name,
                "RDR1"."Quantity" as quantity,
                "RDR1"."Price" as price
            FROM "ORDR"
            JOIN "RDR1" ON "ORDR"."DocEntry" = "RDR1"."DocEntry"
            WHERE "ORDR"."DocStatus" = 'O'
            ORDER BY "ORDR"."DocNum"
        """
        response = requests.get(
            f"{BASE_URL}/query",
            params={"sql": sql}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@tool
def get_closed_orders() -> dict:
    """
    Get all closed sales orders.
    Use when user asks for closed or completed orders.
    """
    try:
        sql = """
            SELECT 
                "ORDR"."DocNum" as order_number,
                "ORDR"."DocDate" as date,
                "ORDR"."CardName" as customer_name,
                "ORDR"."DocTotal" as total,
                "RDR1"."ItemName" as item_name,
                "RDR1"."Quantity" as quantity,
                "RDR1"."Price" as price
            FROM "ORDR"
            JOIN "RDR1" ON "ORDR"."DocEntry" = "RDR1"."DocEntry"
            WHERE "ORDR"."DocStatus" = 'C'
            ORDER BY "ORDR"."DocNum"
        """
        response = requests.get(
            f"{BASE_URL}/query",
            params={"sql": sql}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@tool
def get_order_summary() -> dict:
    """
    Get summary of all sales orders.
    Use when user asks for total, count or summary.
    """
    try:
        sql = """
            SELECT 
                COUNT(*) as total_orders,
                SUM("DocTotal") as total_amount,
                COUNT(CASE WHEN "DocStatus"='O' 
                      THEN 1 END) as open_orders,
                COUNT(CASE WHEN "DocStatus"='C' 
                      THEN 1 END) as closed_orders
            FROM "ORDR"
        """
        response = requests.get(
            f"{BASE_URL}/query",
            params={"sql": sql}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@tool
def get_orders_by_item(item_name: str) -> dict:
    """
    Get all orders containing a specific item.
    item_name: Name of the item to search
    """
    try:
        sql = f"""
            SELECT 
                "ORDR"."DocNum" as order_number,
                "ORDR"."DocDate" as date,
                "ORDR"."CardName" as customer_name,
                "ORDR"."DocTotal" as total,
                "RDR1"."ItemName" as item_name,
                "RDR1"."Quantity" as quantity,
                "RDR1"."Price" as price
            FROM "ORDR"
            JOIN "RDR1" ON "ORDR"."DocEntry" = "RDR1"."DocEntry"
            WHERE "RDR1"."ItemName" ILIKE '%{item_name}%'
            ORDER BY "ORDR"."DocNum"
        """
        response = requests.get(
            f"{BASE_URL}/query",
            params={"sql": sql}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@tool
def get_customer_info(customer_name: str) -> dict:
    """
    Get customer information including credit limit.
    customer_name: Name of the customer
    """
    try:
        sql = f"""
            SELECT 
                "CardCode" as customer_code,
                "CardName" as customer_name,
                "Phone" as phone,
                "Email" as email,
                "Address" as address,
                "CreditLimit" as credit_limit,
                "Balance" as balance
            FROM "OCRD"
            WHERE "CardName" ILIKE '%{customer_name}%'
        """
        response = requests.get(
            f"{BASE_URL}/query",
            params={"sql": sql}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@tool
def get_item_info(item_name: str) -> dict:
    """
    Get item information including stock and price.
    item_name: Name of the item
    """
    try:
        sql = f"""
            SELECT 
                "ItemCode" as item_code,
                "ItemName" as item_name,
                "Price" as price,
                "Stock" as stock,
                "ItemGroup" as item_group
            FROM "OITM"
            WHERE "ItemName" ILIKE '%{item_name}%'
        """
        response = requests.get(
            f"{BASE_URL}/query",
            params={"sql": sql}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 🤖 BUILD FETCH AGENT
# ─────────────────────────────────────────────

fetch_tools = [
    get_all_orders,
    get_orders_by_customer,
    get_open_orders,
    get_closed_orders,
    get_order_summary,
    get_orders_by_item,
    get_customer_info,
    get_item_info
]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

fetch_agent = create_react_agent(
    model=llm,
    tools=fetch_tools,
    prompt="""You are a Sales Order Fetch Agent for SAP Business One.
    You help users query and retrieve sales order data.

    You have access to these tools:
    - get_all_orders: Get all sales orders
    - get_orders_by_customer: Get orders for specific customer
    - get_open_orders: Get all open/pending orders
    - get_closed_orders: Get all closed/completed orders
    - get_order_summary: Get total count and amount summary
    - get_orders_by_item: Get orders containing specific item
    - get_customer_info: Get customer details
    - get_item_info: Get item details and stock

    IMPORTANT RULES:
    - Always understand what the user is asking
    - Use the correct tool based on the question
    - Always explain results in simple friendly language
    - Show data in a clear readable format
    - If data has multiple rows explain each one clearly

    Examples:
    - "Show all orders" → use get_all_orders
    - "Orders for Rahul" → use get_orders_by_customer
    - "How many open orders?" → use get_open_orders
    - "Total sales amount?" → use get_order_summary
    - "Orders with Laptop?" → use get_orders_by_item
    - "Tell me about customer Priya" → use get_customer_info
    - "Is Laptop in stock?" → use get_item_info
    """
)


def run_fetch_agent(user_message: str) -> str:
    """Run the fetch agent with a user message"""
    result = fetch_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content