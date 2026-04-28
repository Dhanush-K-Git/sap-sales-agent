from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
from agents.sales_order_agent import run_sales_order_agent
from agents.sales_invoice_agent import run_sales_invoice_agent
from agents.sales_return_agent import run_sales_return_agent

load_dotenv()

# ─────────────────────────────────────────────
# 🧠 THE SUPERVISOR AGENT
# ─────────────────────────────────────────────

# The LLM brain for supervisor
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)


def route_message(user_message: str) -> str:
    """
    Supervisor reads the user message and decides
    which agent should handle it
    Returns: 'order', 'invoice', or 'return'
    """

    system_prompt = """You are a supervisor that routes user messages 
    to the correct sales agent.
    
    You have 3 agents available:
    - 'order'   : Handles sales orders (creating, reading, updating, 
                  cancelling, closing orders)
    - 'invoice' : Handles sales invoices (creating, reading, updating, 
                  cancelling invoices)
    - 'return'  : Handles sales returns (creating, reading, updating, 
                  cancelling returns)
    
    Read the user message carefully and reply with ONLY one word:
    either 'order', 'invoice', or 'return'
    
    Nothing else. Just one word.
    
    Examples:
    - "Create a sales order for C001" -> order
    - "Show me invoice 123" -> invoice
    - "I want to return items" -> return
    - "Cancel order 456" -> order
    - "Get all invoices" -> invoice
    - "Create a return for customer C002" -> return
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages)
    
    # Clean the response - just get the one word
    route = response.content.strip().lower()
    
    # Safety check - if unexpected response default to order
    if route not in ["order", "invoice", "return"]:
        route = "order"
    
    return route


def run_supervisor(user_message: str) -> str:
    """
    Main function - takes user message,
    routes it to correct agent and returns response
    """

    print(f"\n{'='*50}")
    print(f"User: {user_message}")
    print(f"{'='*50}")

    # Step 1: Supervisor decides which agent to call
    route = route_message(user_message)
    print(f"Supervisor Decision: Routing to → {route.upper()} agent")
    print(f"{'='*50}\n")

    # Step 2: Call the correct agent
    if route == "order":
        response = run_sales_order_agent(user_message)

    elif route == "invoice":
        response = run_sales_invoice_agent(user_message)

    elif route == "return":
        response = run_sales_return_agent(user_message)

    return response