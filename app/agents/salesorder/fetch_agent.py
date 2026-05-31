# app/agents/salesorder/fetch_agent.py
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from app.operations.llm_config import llm_fetch as llm
from app.operations.schema_rag import get_schema_from_rag
from app.operations.utils import execute_query

load_dotenv()


@tool
def get_all_customers() -> dict:
    """Get complete list of all customers from SAP B1."""
    sql = """SELECT
        "CardCode", "CardName", "CardType",
        "Phone1", "Balance", "CreditLine", "Address"
        FROM OCRD
        WHERE "CardType" = 'C'
        ORDER BY "CardCode"
    """
    return execute_query(sql)

@tool
def search_customers(search_term: str) -> dict:
    """
    Search customers by code or name.
    search_term: Any part of customer name or code
    """
    sql = f"""SELECT
        "CardCode", "CardName", "Phone1",
        "Balance", "CreditLine", "Address"
        FROM OCRD
        WHERE "CardType" = 'C'
        AND (
            "CardName" LIKE '%{search_term}%'
            OR "CardCode" LIKE '%{search_term}%'
        )
        ORDER BY "CardName"
    """
    return execute_query(sql)


@tool
def get_customer_info(customer_name: str) -> dict:
    """Get details for a specific customer by name."""
    sql = f"""SELECT
        "CardCode", "CardName", "Phone1",
        "Balance", "CreditLine", "Address"
        FROM OCRD
        WHERE "CardName" LIKE '%{customer_name}%'
        AND "CardType" = 'C'
    """
    return execute_query(sql)


@tool
def get_all_items() -> dict:
    """Get complete list of all items/products from SAP B1."""
    sql = """SELECT
        "ItemCode", "ItemName", "OnHand",
        "AvgPrice", "SellItem", "InvntItem"
        FROM OITM
        WHERE "SellItem" = 'Y'
        ORDER BY "ItemCode"
    """
    return execute_query(sql)


@tool
def get_item_info(item_name: str) -> dict:
    """Get stock and price for a specific item by name."""
    sql = f"""SELECT
        "ItemCode", "ItemName", "OnHand",
        "AvgPrice", "SellItem"
        FROM OITM
        WHERE "ItemName" LIKE '%{item_name}%'
    """
    return execute_query(sql)


@tool
def get_all_orders() -> dict:
    """Get all sales orders from SAP B1."""
    sql = """SELECT
        T0."DocNum", T0."DocDate", T0."DocDueDate",
        T0."CardCode", T0."CardName",
        T0."DocTotal", T0."DocStatus", T0."DocCur",
        T1."ItemCode", T1."Dscription",
        T1."Quantity", T1."Price"
        FROM ORDR T0
        INNER JOIN RDR1 T1 ON T0."DocEntry" = T1."DocEntry"
        ORDER BY T0."DocNum" DESC
    """
    return execute_query(sql)


@tool
def get_orders_by_customer(customer_name: str) -> dict:
    """Get all orders for a specific customer."""
    sql = f"""SELECT
        T0."DocNum", T0."DocDate",
        T0."CardCode", T0."CardName",
        T0."DocTotal", T0."DocStatus",
        T1."ItemCode", T1."Dscription",
        T1."Quantity", T1."Price"
        FROM ORDR T0
        INNER JOIN RDR1 T1 ON T0."DocEntry" = T1."DocEntry"
        WHERE T0."CardName" LIKE '%{customer_name}%'
        ORDER BY T0."DocNum" DESC
    """
    return execute_query(sql)


@tool
def get_open_orders() -> dict:
    """Get all open/pending sales orders."""
    sql = """SELECT
        T0."DocNum", T0."DocDate", T0."DocDueDate",
        T0."CardCode", T0."CardName",
        T0."DocTotal", T0."DocStatus",
        T1."ItemCode", T1."Dscription", T1."Quantity"
        FROM ORDR T0
        INNER JOIN RDR1 T1 ON T0."DocEntry" = T1."DocEntry"
        WHERE T0."DocStatus" = 'O'
        ORDER BY T0."DocNum" DESC
    """
    return execute_query(sql)


@tool
def get_order_summary() -> dict:
    """Get total statistics for all sales orders."""
    sql = """SELECT
        COUNT(*) AS TotalOrders,
        SUM("DocTotal") AS TotalValue,
        SUM(CASE WHEN "DocStatus"='O' THEN 1 ELSE 0 END) AS OpenOrders,
        SUM(CASE WHEN "DocStatus"='C' THEN 1 ELSE 0 END) AS ClosedOrders,
        AVG("DocTotal") AS AvgOrderValue,
        MAX("DocTotal") AS HighestOrder,
        MIN("DocTotal") AS LowestOrder
        FROM ORDR
    """
    return execute_query(sql)


@tool
def text_to_sql_with_rag(question: str) -> dict:
    """
    Use for complex analytical questions.
    RAG finds schema, Claude generates SQL,
    runs against Sir's SAP HANA API.
    """
    try:
        schema_context = get_schema_from_rag(question)
        from app.operations.llm_config import get_llm
        sql_llm = get_llm(max_tokens=512)

        prompt = f"""You are a SAP HANA SQL expert for SAP Business One.
Generate ONLY a valid SQL SELECT query. No explanation, no markdown.

SAP B1 TABLES AND EXACT COLUMN NAMES:
- ORDR (Sales Orders): DocNum, DocDate, DocDueDate, CardCode,
  CardName, DocTotal, DocStatus, DocCur, CANCELED
- RDR1 (Order Lines): DocEntry, ItemCode, Dscription,
  Quantity, Price, LineTotal
- OCRD (Customers): CardCode, CardName, CardType,
  Phone1, Balance, CreditLine, Address
- OITM (Items): ItemCode, ItemName, OnHand,
  AvgPrice, SellItem

ADDITIONAL SCHEMA FROM RAG:
{schema_context}

RULES:
- Use double quotes around column names
- Use T0, T1 aliases for table joins
- Use INNER JOIN for joining tables
- Use TOP N to limit results (e.g. TOP 20)
- Use LIKE for text search (not ILIKE)
- DocStatus: O=Open, C=Closed
- CANCELED: Y=Cancelled, N=Not cancelled
- Join ORDR and RDR1 on DocEntry

USER QUESTION: {question}

SQL QUERY:"""

        response = sql_llm.invoke([HumanMessage(content=prompt)])
        generated_sql = response.content.strip()
        generated_sql = generated_sql.replace("```sql","").replace("```","").strip()
        print(f"\n[RAG SQL] {generated_sql}\n")

        result = execute_query(generated_sql)
        result["generated_sql"] = generated_sql
        return result

    except Exception as e:
        return {"error": str(e)}


fetch_tools = [
    text_to_sql_with_rag,
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

RESPONSE FORMAT - FOLLOW STRICTLY:
1. Greeting and report title
2. SUMMARY section with key numbers
3. Clean MARKDOWN TABLE with proper columns
4. KEY INSIGHTS at the end

FORMAT RULES:
- NO emojis anywhere
- Professional business language only
- Use Rs. for all currency amounts
- Status: [Open] or [Closed] or [Pending]
- Bold important numbers using **value**
- Separate sections with ---
- Always calculate totals and averages
- Always add business insights

FOR CUSTOMER QUERIES:
| Code | Customer Name | Phone | Credit Limit | Balance | Address |

FOR ORDER QUERIES:
| Order No | Date | Customer | Item | Qty | Price | Total | Status |

FOR ITEM QUERIES:
| Item Code | Item Name | Stock | Price | Status |

FOR SUMMARY:
- Total count and total value
- Open vs Closed breakdown
- Average order value
- Highest and lowest
- What needs attention

TOOLS:
- get_all_customers      - list all customers
- get_customer_info      - one specific customer
- get_all_items          - list all products
- get_item_info          - one specific item
- get_all_orders         - all sales orders
- get_orders_by_customer - orders for one customer
- get_open_orders        - pending orders only
- get_order_summary      - statistics and totals
- text_to_sql_with_rag   - complex questions

ALWAYS use a tool before responding.
NEVER say data is unavailable without trying a tool."""
)


def run_fetch_agent(user_message: str) -> str:
    """Run the fetch agent with user message."""
    result = fetch_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content