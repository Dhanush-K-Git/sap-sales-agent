from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
import requests
from dotenv import load_dotenv
from app.operations.utils import execute_query

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)


@tool
def get_all_customers() -> dict:
    """Get the complete list of all customers."""
    sql = """
        SELECT "CardCode", "CardName", "Phone", "Email", "CreditLimit", "Balance"
        FROM "OCRD"
        ORDER BY "CardCode"
    """
    return execute_query(sql)


@tool
def get_customer_info(customer_name: str) -> dict:
    """Get details for a specific customer by name."""
    sql = f"""
        SELECT "CardCode", "CardName", "Phone", "Email", "CreditLimit", "Balance"
        FROM "OCRD"
        WHERE "CardName" ILIKE '%{customer_name}%'
    """
    return execute_query(sql)


@tool
def get_all_items() -> dict:
    """Get the complete list of all items/products."""
    sql = """
        SELECT "ItemCode", "ItemName", "Price", "Stock", "ItemGroup"
        FROM "OITM"
        ORDER BY "ItemCode"
    """
    return execute_query(sql)


@tool
def get_item_info(item_name: str) -> dict:
    """Get stock and price for a specific item by name."""
    sql = f"""
        SELECT "ItemCode", "ItemName", "Price", "Stock", "ItemGroup"
        FROM "OITM"
        WHERE "ItemName" ILIKE '%{item_name}%'
    """
    return execute_query(sql)


@tool
def get_all_orders() -> dict:
    """Get all sales orders with customer and item details."""
    sql = """
        SELECT
            o."DocNum"  AS order_number,
            o."DocDate" AS date,
            o."CardName" AS customer_name,
            o."DocTotal" AS total,
            o."DocStatus" AS status,
            l."ItemName" AS item_name,
            l."Quantity" AS quantity,
            l."Price"    AS price
        FROM "ORDR" o
        JOIN "RDR1" l ON o."DocEntry" = l."DocEntry"
        ORDER BY o."DocNum"
    """
    return execute_query(sql)


@tool
def get_orders_by_customer(customer_name: str) -> dict:
    """Get all orders for a specific customer by name."""
    sql = f"""
        SELECT
            o."DocNum"   AS order_number,
            o."DocDate"  AS date,
            o."CardName" AS customer_name,
            o."DocTotal" AS total,
            o."DocStatus" AS status,
            l."ItemName" AS item_name,
            l."Quantity" AS quantity
        FROM "ORDR" o
        JOIN "RDR1" l ON o."DocEntry" = l."DocEntry"
        WHERE o."CardName" ILIKE '%{customer_name}%'
        ORDER BY o."DocNum"
    """
    return execute_query(sql)


@tool
def get_open_orders() -> dict:
    """Get all open (pending) sales orders."""
    sql = """
        SELECT
            o."DocNum"   AS order_number,
            o."DocDate"  AS date,
            o."CardName" AS customer_name,
            o."DocTotal" AS total,
            l."ItemName" AS item_name,
            l."Quantity" AS quantity
        FROM "ORDR" o
        JOIN "RDR1" l ON o."DocEntry" = l."DocEntry"
        WHERE o."DocStatus" = 'O'
        ORDER BY o."DocNum"
    """
    return execute_query(sql)


@tool
def get_order_summary() -> dict:
    """Get total count and value statistics for all orders."""
    sql = """
        SELECT
            COUNT(*) AS total_orders,
            SUM("DocTotal") AS total_amount,
            COUNT(CASE WHEN "DocStatus"='O' THEN 1 END) AS open_orders,
            COUNT(CASE WHEN "DocStatus"='C' THEN 1 END) AS closed_orders
        FROM "ORDR"
    """
    return execute_query(sql)


fetch_tools = [
    get_all_customers,
    get_customer_info,
    get_all_items,
    get_item_info,
    get_all_orders,
    get_orders_by_customer,
    get_open_orders,
    get_order_summary,
]

fetch_agent = create_react_agent(
    model=llm,
    tools=fetch_tools,
    prompt="""You are Alex, a friendly SAP B1 Sales Assistant at Techative Pvt Ltd Solutions.

TOOLS AND WHEN TO USE THEM:
- get_all_customers      → "list customers", "show all customers", "who are our customers"
- get_customer_info      → "tell me about customer X", "details of John"
- get_all_items          → "list items", "show products", "what do we sell"
- get_item_info          → "price of Laptop", "stock for Mouse"
- get_all_orders         → "show all orders", "list orders"
- get_orders_by_customer → "orders for customer X"
- get_open_orders        → "open orders", "pending orders"
- get_order_summary      → "summary", "statistics", "how many orders"

RULES:
- ALWAYS call a tool first before saying you cannot help
- Never say data is unavailable without trying a tool
- Present results in a clean, friendly format with bullet points
- If a tool returns an error, show the error message clearly
"""
)


def run_fetch_agent(user_message: str) -> str:
    """Run the fetch agent with user message."""
    result = fetch_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content