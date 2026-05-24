# Add this import at the top of fetch_agent.py
from app.operations.llm_config import llm_fetch as llm
from app.operations.sap_client import sap_get # You'll need to add a GET function to sap_client.py
from app.operations.schema_rag import get_schema_from_rag
import os
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
import requests
from dotenv import load_dotenv
from app.operations.utils import execute_query

load_dotenv()

from app.operations.llm_config import llm_fetch


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

@tool
def text_to_sql_with_rag(question: str) -> dict:
    """
    Use this for ANY complex or custom question not covered by
    the other tools. Uses RAG to find relevant schema, then
    generates and runs the correct SQL automatically.
    question: Any natural language question about sales data
    """
    try:
        # STEP 1 — RAG: find relevant schema for this question
        schema_context = get_schema_from_rag(question)

        # STEP 2 — LLM: generate SQL from question + schema
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage

        sql_llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        )

        prompt = f"""You are a PostgreSQL expert.
Generate ONLY a valid SQL SELECT query. No explanation, no markdown, no backticks.

DATABASE SCHEMA (relevant tables and columns):
{schema_context}

IMPORTANT RULES:
- All table and column names MUST be in double quotes e.g. "ORDR", "CardName"
- Use ILIKE for case-insensitive text search
- Always use SELECT, never INSERT/UPDATE/DELETE
- For joins: ORDR joins RDR1 on "DocEntry"
- For joins: OCRD has customer info (CardCode, CardName)

USER QUESTION: {question}

SQL QUERY:"""

        response = sql_llm.invoke([HumanMessage(content=prompt)])
        generated_sql = response.content.strip()

        # Clean up if LLM adds backticks anyway
        generated_sql = generated_sql.replace("```sql", "").replace("```", "").strip()

        print(f"\n[RAG] Generated SQL:\n{generated_sql}\n")

        # STEP 3 — Execute the generated SQL
        result = execute_query(generated_sql)
        result["generated_sql"] = generated_sql
        result["schema_used"] = schema_context
        return result

    except Exception as e:
        return {"error": str(e)}


fetch_tools = [
    text_to_sql_with_rag,    # ← RAG-powered text-to-SQL (for complex questions)
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
prompt="""You are Alex, a professional SAP B1 Sales Intelligence Assistant
at Techative Pvt Ltd Solutions.

Sir instruction: The response from the agent is the main thing to impress clients.

RESPONSE FORMAT RULES - FOLLOW STRICTLY:

1. Always start with a greeting and report title.
   Example: Hello! Here is your Customer Master Report.

2. Always show a SUMMARY section first:
   SUMMARY
   --------------------------
   Total Orders   : 10
   Open Orders    : 6
   Closed Orders  : 4
   Total Value    : Rs.12,50,000
   --------------------------

3. Always show data in a clean MARKDOWN TABLE with proper columns.

4. Always end with KEY INSIGHTS section:
   KEY INSIGHTS
   - Highest order : Order 1001 - Rs.1,00,000
   - Most active   : C001 with 3 orders
   - Attention     : 6 open orders pending

FORMAT RULES:
   - NO emojis anywhere in the response
   - Professional business language only
   - Use Rs. for all currency amounts
   - Status must show as [Open] or [Closed] or [Pending]
   - Stock status: [In Stock] or [Low Stock] or [Out of Stock]
   - Bold important numbers using **value**
   - Separate sections with ---
   - Always calculate and show totals and averages
   - Always add business insights at the end

FOR CUSTOMER QUERIES show these columns:
   Code | Customer Name | Phone | Credit Limit | Balance | Available Credit | Utilization %

FOR ORDER QUERIES show these columns:
   Order No | Date | Customer | Item | Qty | Unit Price | Total | Status

FOR ITEM QUERIES show these columns:
   Item Code | Item Name | Price | Stock | Stock Status

FOR INVOICE QUERIES show these columns:
   Invoice No | Date | Customer | Amount | Status

FOR RETURN QUERIES show these columns:
   Return No | Date | Customer | Amount | Status

FOR SUMMARY AND ANALYTICS show:
   - Total count and total value
   - Open vs Closed breakdown
   - Average value
   - Highest and lowest
   - What needs attention

TOOLS TO USE:
   - get_all_customers      - list customers, show customers
   - get_customer_info      - details of one specific customer
   - get_all_items          - list items, show all products
   - get_item_info          - price or stock of one item
   - get_all_orders         - show all orders
   - get_orders_by_customer - orders for a specific customer
   - get_open_orders        - open orders, pending orders
   - get_order_summary      - summary, statistics, totals
   - text_to_sql_with_rag   - complex analytical questions

NEVER say data is unavailable without trying a tool first.
NEVER give plain text data dumps.
ALWAYS format every response as a proper professional business report.
ALWAYS use a tool before responding.
"""
)


def run_fetch_agent(user_message: str) -> str:
    """Run the fetch agent with user message."""
    result = fetch_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content