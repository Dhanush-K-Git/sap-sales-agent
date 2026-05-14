from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
import requests
from dotenv import load_dotenv
from app.operations.utils import execute_query

load_dotenv()

BASE_URL = "https://sap-sales-agent-1.onrender.com"
PRODUCTION_API = "http://vzone.in:1662/api/GetMethod/GetData"

# 🤖 LLM SETUP ← THIS MUST BE HERE!
# ─────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)


# ─────────────────────────────────────────────
# 🔧 FETCH TOOLS
# ─────────────────────────────────────────────

@tool
def text_to_sql_query(question: str) -> dict:
    """
    Convert natural language to SQL and fetch
    from production SAP B1 database.
    question: Any question about sales data
    """
    try:
        response = requests.post(
            f"{BASE_URL}/generate-sql/",
            params={"query": question}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@tool
def get_all_orders() -> dict:
    """Get all sales orders."""
    sql = """
        SELECT 
            ORDR.DocNum as order_number,
            ORDR.DocDate as date,
            ORDR.CardName as customer_name,
            ORDR.DocTotal as total,
            ORDR.DocStatus as status,
            RDR1.ItemName as item_name,
            RDR1.Quantity as quantity,
            RDR1.Price as price
        FROM ORDR
        JOIN RDR1 ON ORDR.DocEntry = RDR1.DocEntry
        ORDER BY ORDR.DocNum
    """
    return execute_query(sql)


@tool
def get_orders_by_customer(customer_name: str) -> dict:
    """
    Get orders for a specific customer.
    customer_name: Customer name to search
    """
    sql = f"""
        SELECT 
            ORDR.DocNum as order_number,
            ORDR.DocDate as date,
            ORDR.CardName as customer_name,
            ORDR.DocTotal as total,
            ORDR.DocStatus as status,
            RDR1.ItemName as item_name,
            RDR1.Quantity as quantity
        FROM ORDR
        JOIN RDR1 ON ORDR.DocEntry = RDR1.DocEntry
        WHERE ORDR.CardName LIKE '%{customer_name}%'
        ORDER BY ORDR.DocNum
    """
    return execute_query(sql)


@tool
def get_open_orders() -> dict:
    """Get all open sales orders."""
    sql = """
        SELECT 
            ORDR.DocNum as order_number,
            ORDR.DocDate as date,
            ORDR.CardName as customer_name,
            ORDR.DocTotal as total,
            RDR1.ItemName as item_name,
            RDR1.Quantity as quantity
        FROM ORDR
        JOIN RDR1 ON ORDR.DocEntry = RDR1.DocEntry
        WHERE ORDR.DocStatus = 'O'
        ORDER BY ORDR.DocNum
    """
    return execute_query(sql)


@tool
def get_order_summary() -> dict:
    """Get summary statistics of all orders."""
    sql = """
        SELECT 
            COUNT(*) as total_orders,
            SUM(DocTotal) as total_amount,
            COUNT(CASE WHEN DocStatus='O' 
                  THEN 1 END) as open_orders,
            COUNT(CASE WHEN DocStatus='C' 
                  THEN 1 END) as closed_orders
        FROM ORDR
    """
    return execute_query(sql)


@tool
def get_customer_info(customer_name: str) -> dict:
    """
    Get customer details.
    customer_name: Customer name
    """
    sql = f"""
        SELECT 
            CardCode, CardName,
            Phone, Email,
            CreditLimit, Balance
        FROM OCRD
        WHERE CardName LIKE '%{customer_name}%'
    """
    return execute_query(sql)


@tool
def get_item_info(item_name: str) -> dict:
    """
    Get item stock and price.
    item_name: Item name
    """
    sql = f"""
        SELECT 
            ItemCode, ItemName,
            Price, Stock, ItemGroup
        FROM OITM
        WHERE ItemName LIKE '%{item_name}%'
    """
    return execute_query(sql)


# ─────────────────────────────────────────────
# 🤖 BUILD FETCH AGENT WITH OLLAMA
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# 🤖 BUILD FETCH AGENT
# ─────────────────────────────────────────────
fetch_tools = [
    text_to_sql_query,
    get_all_orders,
    get_orders_by_customer,
    get_open_orders,
    get_order_summary,
    get_customer_info,
    get_item_info
]

# app/agents/salesorder/fetch_agent.py (and update_agent.py)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# Standardize the return to a string to match the Supervisor's expectations
def run_fetch_agent(user_message: str) -> str:
    result = fetch_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content

fetch_agent = create_react_agent(
    model=llm,
    tools=fetch_tools,
    prompt="""You are Alex, a friendly and knowledgeable 
    SAP B1 Sales Assistant at Techative Pvt Ltd Solutions.

    You help users understand their sales data in a 
    conversational, human-like way just like ChatGPT!

    YOUR PERSONALITY:
    - Friendly and professional 😊
    - Always greet and acknowledge the user
    - Explain data in simple terms
    - Use bullet points for lists
    - Add context and insights to data
    - Never just dump raw data

    TOOLS YOU HAVE:
    1. text_to_sql_query - For complex questions
    2. get_all_orders - Get ALL sales orders
    3. get_orders_by_customer - Orders for ONE customer
    4. get_open_orders - OPEN orders only
    5. get_order_summary - Statistics and totals
    6. get_customer_info - Customer details
    7. get_item_info - Item stock and price

    Always explain results in a friendly way!
    """
)


def run_fetch_agent(user_message: str) -> str:
    """Run the fetch agent with user message"""
    result = fetch_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content