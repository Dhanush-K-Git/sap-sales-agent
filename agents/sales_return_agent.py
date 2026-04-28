from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv
from tools.sap_tools import (
    create_sales_return,
    get_sales_return,
    get_all_sales_returns,
    update_sales_return,
    cancel_sales_return
)

load_dotenv()

# ─────────────────────────────────────────────
# 🔧 WRAP SAP FUNCTIONS AS TOOLS
# ─────────────────────────────────────────────

@tool
def tool_create_sales_return(card_code: str, items: list) -> dict:
    """
    Create a new sales return in SAP B1.
    card_code: Customer code e.g C001
    items: List of items with ItemCode, Quantity, TaxCode, UnitPrice
    """
    cookies = None
    return create_sales_return(card_code, items, cookies)


@tool
def tool_get_sales_return(return_id: int) -> dict:
    """
    Get a specific sales return by its ID number.
    return_id: The SAP return document number e.g 123
    """
    cookies = None
    return get_sales_return(return_id, cookies)


@tool
def tool_get_all_sales_returns() -> dict:
    """
    Get all sales returns from SAP B1.
    """
    cookies = None
    return get_all_sales_returns(cookies)


@tool
def tool_update_sales_return(return_id: int, comments: str) -> dict:
    """
    Update comments on an existing sales return.
    return_id: The SAP return document number
    comments: New comment text to add
    """
    cookies = None
    return update_sales_return(return_id, comments, cookies)


@tool
def tool_cancel_sales_return(return_id: int) -> dict:
    """
    Cancel an existing sales return.
    return_id: The SAP return document number to cancel
    """
    cookies = None
    return cancel_sales_return(return_id, cookies)


# ─────────────────────────────────────────────
# 🤖 BUILD THE SALES RETURN AGENT
# ─────────────────────────────────────────────

# List of all tools this agent can use
sales_return_tools = [
    tool_create_sales_return,
    tool_get_sales_return,
    tool_get_all_sales_returns,
    tool_update_sales_return,
    tool_cancel_sales_return
]

# The LLM brain of the agent
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# Create the agent
sales_return_agent = create_react_agent(
    model=llm,
    tools=sales_return_tools,
    prompt="""You are a Sales Return Agent for SAP Business One.
    Your job is to help users manage sales returns.
    You can create, read, update and cancel sales returns.
    Always be helpful and confirm actions clearly.
    If you need information to complete a task, ask the user for it.
    """
)


def run_sales_return_agent(user_message: str) -> str:
    """Run the sales return agent with a user message"""
    result = sales_return_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content