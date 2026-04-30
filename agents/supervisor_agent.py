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
    """
    Supervisor reads the user message and decides
    which agent should handle it
    """
    system_prompt = """You are a supervisor that routes 
    user messages to the correct sales agent.
    
    You have 4 agents available:
    - 'order'   : Creates, updates, cancels sales orders
    - 'invoice' : Creates, updates, cancels invoices
    - 'return'  : Creates, updates, cancels returns
    - 'fetch'   : Fetches, retrieves, shows, gets data
                  Handles ALL questions about:
                  orders, invoices, returns, customers,
                  items, stock, summary, trends
    
    Read the user message carefully and reply with 
    ONLY one word: 'order', 'invoice', 'return' or 'fetch'
    
    Examples:
    - "Create a sales order" -> order
    - "Show me all orders" -> fetch
    - "Get orders for Rahul" -> fetch
    - "How many open orders?" -> fetch
    - "What is total sales?" -> fetch
    - "Cancel order 123" -> order
    - "Create an invoice" -> invoice
    - "Show all invoices" -> fetch
    - "Create a return" -> return
    - "Is Laptop in stock?" -> fetch
    - "Tell me about customer Priya" -> fetch
    - "Show me closed orders" -> fetch
    """

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
    """
    Main function - takes user message,
    routes it to correct agent and returns response
    """
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