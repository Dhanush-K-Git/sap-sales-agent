from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
from agents.sales_order_agent import run_sales_order_agent
from agents.sales_invoice_agent import run_sales_invoice_agent
from agents.sales_return_agent import run_sales_return_agent
from agents.fetch_agent import run_fetch_agent

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)


def route_message(user_message: str) -> str:
    system_prompt = (
        "You are a supervisor that routes user messages "
        "to the correct sales agent. "
        "You have 4 agents available: "
        "'order': Creates, updates, cancels, closes, validates sales orders. "
        "'invoice': Creates, updates, cancels invoices. "
        "'return': Creates, updates, cancels returns. "
        "'fetch': Fetches, retrieves, shows data. "
        "Read the user message carefully and reply with "
        "ONLY one word: 'order', 'invoice', 'return' or 'fetch'. "
        "Examples: "
        "Create a sales order -> order. "
        "Update order 123 -> order. "
        "Cancel order 456 -> order. "
        "Close order 789 -> order. "
        "Validate customer C001 -> order. "
        "Check stock for Laptop -> order. "
        "Show me all orders -> fetch. "
        "Get all invoices -> fetch. "
        "Create an invoice -> invoice. "
        "Create a return -> return."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages)
    route = response.content.strip().lower()

    if route not in ["order", "invoice", "return", "fetch"]:
        route = "fetch"

    return route


def run_supervisor(user_message: str) -> str:
    print(f"\n{'='*50}")
    print(f"User: {user_message}")
    print(f"{'='*50}")

    route = route_message(user_message)
    print(f"Supervisor Decision: Routing to → {route.upper()} agent")
    print(f"{'='*50}\n")

    if route == "order":
        response = run_sales_order_agent(user_message)
    elif route == "invoice":
        response = run_sales_invoice_agent(user_message)
    elif route == "return":
        response = run_sales_return_agent(user_message)
    elif route == "fetch":
        response = run_fetch_agent(user_message)

    return response