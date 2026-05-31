from fastapi import APIRouter
from groq import Groq
import os
import time
import requests
from dotenv import load_dotenv
from app.operations.schema_rag import get_schema_from_rag

load_dotenv()

router = APIRouter()

# ─────────────────────────────────────────────
# 🔑 GROQ CLIENT
# ─────────────────────────────────────────────
groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ─────────────────────────────────────────────
# 🌍 PRODUCTION API
# ─────────────────────────────────────────────
PRODUCTION_API = "http://vzone.in:1662/api/GetMethod/GetData"
BASE_URL = "https://sap-sales-agent-1.onrender.com"


def generate_sql_with_rag(query: str) -> dict:
    """
    Generate SQL using RAG schema mapping + Groq LLM
    """
    # Step 1: Get relevant schema from RAG
    schema_context = get_schema_from_rag(query)

    # Step 2: Generate SQL using Groq
    prompt = f"""You are a SAP B1 SQL expert assistant.
Your job is to convert natural language questions 
into accurate SQL queries.

IMPORTANT RULES:
- Use ONLY the tables and columns provided in schema
- Output ONLY the SQL query, nothing else
- No explanation, no markdown, no backticks
- Always JOIN ORDR with RDR1 using DocEntry
  when both tables are needed
- Use proper SQL syntax

SCHEMA (use ONLY these):
{schema_context}

QUESTION: {query}

SQL QUERY:"""

    response = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a SQL expert. Output only the SQL query with no explanation."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=300
    )

    sql = response.choices[0].message.content.strip()

    # Clean SQL
    if "```sql" in sql:
        sql = sql.split("```sql")[1].split("```")[0].strip()
    elif "```" in sql:
        sql = sql.split("```")[1].split("```")[0].strip()

    return {
        "sql": sql,
        "schema_used": schema_context
    }


def execute_on_production(sql: str) -> dict:
    """Execute SQL on production API"""
    try:
        response = requests.get(
            PRODUCTION_API,
            params={"query": sql}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def execute_on_our_db(sql: str) -> dict:
    """Execute SQL on our Render database"""
    try:
        response = requests.get(
            f"{BASE_URL}/query",
            params={"sql": sql}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@router.post("/generate-sql/")
def generate_sql(query: str):
    """
    RAG-based Text to SQL endpoint
    1. Maps schema using ChromaDB RAG
    2. Generates SQL using Groq LLM
    3. Executes on database
    """
    start_time = time.time()

    # Generate SQL with RAG
    result = generate_sql_with_rag(query)
    sql = result["sql"]
    schema = result["schema_used"]

    # Try production API first, fallback to our DB
    try:
        data = execute_on_production(sql)
        source = "production"
    except Exception:
        data = execute_on_our_db(sql)
        source = "our_database"

    end_time = time.time()

    return {
        "query": query,
        "schema_mapped": schema,
        "sql_generated": sql,
        "data": data,
        "source": source,
        "time_taken": round(end_time - start_time, 2)
    }