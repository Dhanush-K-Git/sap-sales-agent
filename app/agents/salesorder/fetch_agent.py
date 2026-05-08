from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv
from app.operations.utils import execute_query

load_dotenv()


@tool
def get_all_orders() -> dict:
    """Get all sales orders from database."""
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
    return execute_query(sql)


@tool
def get_orders_by_customer(customer_name: str) -> dict:
    """
    Get all orders for a specific customer.
    customer_name: Name of the customer
    """
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
    return execute_query(sql)


@tool
def get_open_orders() -> dict:
    """Get all open sales orders."""
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
    return execute_query(sql)


@tool
def get_closed_orders() -> dict:
    """Get all closed sales orders."""
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
    return execute_query(sql)


@tool
def get_order_summary() -> dict:
    """Get summary of all sales orders."""
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
    return execute_query(sql)


@tool
def get_orders_by_item(item_name: str) -> dict:
    """
    Get all orders containing a specific item.
    item_name: Name of the item
    """
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
    return execute_query(sql)


@tool
def get_customer_info(customer_name: str) -> dict:
    """
    Get customer information.
    customer_name: Name of the customer
    """
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
    return execute_query(sql)


@tool
def get_item_info(item_name: str) -> dict:
    """
    Get item information including stock.
    item_name: Name of the item
    """
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
    return execute_query(sql)


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
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

fetch_agent = create_react_agent(
    model=llm,
    tools=fetch_tools,
    prompt="""You are a Sales Order Fetch Agent.
    You help users query and retrieve sales data.

    AVAILABLE TOOLS:
    1. get_all_orders - Shows ALL orders
    2. get_orders_by_customer - Orders for ONE customer
    3. get_open_orders - OPEN orders only
    4. get_closed_orders - CLOSED orders only
    5. get_order_summary - COUNT and TOTAL AMOUNT
    6. get_orders_by_item - Orders with ONE item
    7. get_customer_info - Customer details
    8. get_item_info - Item stock and price

    Always pick correct tool and explain results clearly!
    """
)


def run_fetch_agent(user_message: str) -> str:
    result = fetch_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content