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
    cancel_sales_return,
    delete_sales_return
)

load_dotenv()


@tool
def tool_create_sales_return(card_code: str, items: list) -> dict:
    """
    Create a new sales return.
    card_code: Customer code e.g C001
    items: List of items with item_code, quantity, tax_code, unit_price
    """
    return create_sales_return(card_code, items)


@tool
def tool_get_sales_return(return_id: int) -> dict:
    """
    Get a specific sales return by its ID number.
    return_id: The return document number e.g 123
    """
    return get_sales_return(return_id)


@tool
def tool_get_all_sales_returns() -> dict:
    """
    Get all sales returns.
    """
    return get_all_sales_returns()


@tool
def tool_update_sales_return(return_id: int, comments: str) -> dict:
    """
    Update comments on an existing sales return.
    return_id: The return document number
    comments: New comment text to add
    """
    return update_sales_return(return_id, comments)


@tool
def tool_cancel_sales_return(return_id: int) -> dict:
    """
    Cancel an existing sales return.
    return_id: The return document number to cancel
    """
    return cancel_sales_return(return_id)


@tool
def tool_delete_sales_return(return_id: int) -> dict:
    """
    Delete an existing sales return.
    return_id: The return document number to delete
    """
    return delete_sales_return(return_id)


# List of all tools
sales_return_tools = [
    tool_create_sales_return,
    tool_get_sales_return,
    tool_get_all_sales_returns,
    tool_update_sales_return,
    tool_cancel_sales_return,
    tool_delete_sales_return
]

# LLM brain
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# Create agent
sales_return_agent = create_react_agent(
    model=llm,
    tools=sales_return_tools,
    prompt="""You are a Sales Return Agent for SAP Business One.
    Your job is to help users manage sales returns.
    You can create, read, update, cancel and delete sales returns.
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