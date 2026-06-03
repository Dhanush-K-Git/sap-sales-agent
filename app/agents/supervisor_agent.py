# app/agents/supervisor_agent.py

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from app.operations.llm_config import llm_supervisor as llm
from app.operations.memory_store import build_short_term_context
from app.agents.salesorder.sales_order_agent import run_sales_order_agent
from app.agents.salesinvoice.sales_invoice_agent import run_sales_invoice_agent
from app.agents.salesreturn.sales_return_agent import run_sales_return_agent
from app.agents.salesorder.fetch_agent import run_fetch_agent

load_dotenv()


def route_message(user_message: str) -> str:
    """Classify intent into one category."""
    system_prompt = (
        "You are a routing supervisor for SAP B1 at Techative Pvt Ltd. "
        "Classify into ONE word only: order, invoice, return, fetch. "
        "order   = create/update/cancel/close a sales order. "
        "invoice = anything about invoices. "
        "return  = anything about returns. "
        "fetch   = view/list/show/analytics/customers/items. "
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


async def run_supervisor_with_memory(
    user_message: str,
    chat_history: list = None
) -> str:
    """
    Main entry point with SHORT TERM memory.
    Long term memory is handled in streamlit_app.py
    """
    if not user_message or str(user_message).strip() == "":
        return "I did not receive a message. What can I help you with?"

    if chat_history is None:
        chat_history = []

    # Build short term context from recent messages
    short_term_context = build_short_term_context(
        chat_history,
        max_exchanges=5
    )

    # Combine current message with history context
    full_message = user_message
    if short_term_context:
        full_message = f"{user_message}{short_term_context}"

    route = route_message(user_message)
    print(f"\n--- ROUTING: '{user_message}' → {route.upper()} ---")

    try:
        if route == "order":
            return run_sales_order_agent(full_message)
        elif route == "invoice":
            return run_sales_invoice_agent(full_message)
        elif route == "return":
            return run_sales_return_agent(full_message)
        else:
            return run_fetch_agent(full_message)
    except Exception as e:
        print(f"Supervisor Error: {e}")
        return f"Error: {str(e)}"


async def run_supervisor(user_message: str) -> str:
    """Backward compatibility."""
    return await run_supervisor_with_memory(user_message, [])