# app/agents/supervisor_agent.py
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from app.operations.llm_config import llm_supervisor as llm
from app.agents.salesorder.sales_order_agent import run_sales_order_agent
from app.agents.salesinvoice.sales_invoice_agent import run_sales_invoice_agent
from app.agents.salesreturn.sales_return_agent import run_sales_return_agent
from app.agents.salesorder.fetch_agent import run_fetch_agent

load_dotenv()


def route_message(user_message: str) -> str:
    system_prompt = (
        "You are a routing supervisor for SAP B1 at Techative Pvt Ltd. "
        "Classify the user message into ONE category only. "
        "Categories: 'order', 'invoice', 'return', 'fetch'. "
        "order  = create/update/cancel/close a sales order. "
        "invoice = anything about invoices. "
        "return  = anything about returns. "
        "fetch  = view data, list, show, analytics, customers, items. "
        "Reply with ONLY the single category word."
    )
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=str(user_message))
        ])
        route = response.content.strip().lower()
        if route not in ["order", "invoice", "return", "fetch"]:
            return "fetch"
        return route
    except Exception as e:
        print(f"Routing Error: {e}")
        return "fetch"


async def run_supervisor(user_message: str) -> str:
    if not user_message or str(user_message).strip() == "":
        return "I didn't receive a message. What can I help you with?"

    route = route_message(user_message)
    print(f"\n--- ROUTING: '{user_message}' → {route.upper()} ---")

    try:
        if route == "order":
            return run_sales_order_agent(user_message)
        elif route == "invoice":
            return run_sales_invoice_agent(user_message)
        elif route == "return":
            return run_sales_return_agent(user_message)
        else:
            return run_fetch_agent(user_message)
    except Exception as e:
        print(f"Supervisor Error: {e}")
        return f"⚠️ Error: {str(e)}"