import os
import asyncio
from dotenv import load_dotenv
from langchain_groq import ChatGroq
# CRITICAL: These two imports are required to fix the error in image_a2e65a.png
from langchain_core.messages import HumanMessage, SystemMessage

# Sub-agent imports
from app.agents.salesorder.sales_order_agent import run_sales_order_agent
from app.agents.salesinvoice.sales_invoice_agent import run_sales_invoice_agent
from app.agents.salesreturn.sales_return_agent import run_sales_return_agent
from app.agents.salesorder.fetch_agent import run_fetch_agent

load_dotenv()

# Initialize LLM for routing
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def route_message(user_message: str) -> str:
    """Determine which agent handles the request."""
    system_prompt = (
        "You are a routing supervisor for SAP B1. "
        "Categories: 'order', 'invoice', 'return', 'fetch'. "
        "Reply with ONLY the category word."
    )
    # Ensure user_message is never None
    safe_msg = str(user_message) if user_message else "empty"
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=safe_msg)
    ]
    
    try:
        response = llm.invoke(messages)
        route = response.content.strip().lower()
        # Fallback to 'fetch' if LLM provides an invalid category
        if route not in ["order", "invoice", "return", "fetch"]:
            return "fetch"
        return route
    except Exception as e:
        print(f"Routing Error: {e}")
        return "fetch"

async def run_supervisor(user_message: str) -> str:
    """Main entry point for Streamlit UI."""
    if not user_message or str(user_message).strip() == "":
        return "I didn't receive a message. What can I do for you?"

    # 1. Determine Route
    route = route_message(user_message)
    print(f"\n--- DEBUG: Routing '{user_message}' to {route.upper()} agent ---")

    # 2. Construct the State dictionary for Agents
    # Using str(user_message) prevents the Pydantic 'None' validation error
    state = {
        "messages": [HumanMessage(content=str(user_message))],
        "intent": route
    }

    try:
        if route == "order":
            # Sales Order Agent is 'async', so we must 'await' it
            response_dict = await run_sales_order_agent(state)
            return response_dict["messages"][-1].content
        
        elif route == "invoice":
            return run_sales_invoice_agent(user_message)
            
        elif route == "return":
            return run_sales_return_agent(user_message)
            
        else:
            # All other queries (Analytics, Stock, etc.) go to Fetch
            return run_fetch_agent(user_message)
            
    except Exception as e:
        print(f"Execution Error: {e}")
        return f"⚠️ Supervisor Error: {str(e)}"