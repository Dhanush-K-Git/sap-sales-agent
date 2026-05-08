from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv
from app.operations.utils import (
    create_sales_return,
    get_sales_return,
    get_all_sales_returns,
    update_sales_return,
    cancel_sales_return,
    delete_sales_return
)

load_dotenv()


@tool
def tool_create_sales_return(card_code: str,
                              items: list) -> dict:
    """
    Create a new sales return.
    card_code: Customer code e.g C001
    items: List with ItemCode, Quantity, TaxCode, UnitPrice
    """
    return create_sales_return(card_code, items)


@tool
def tool_get_sales_return(return_id: int) -> dict:
    """
    Get a specific return by ID.
    return_id: Return ID number
    """
    return get_sales_return(return_id)


@tool
def tool_get_all_sales_returns() -> dict:
    """Get all sales returns."""
    return get_all_sales_returns()


@tool
def tool_update_sales_return(return_id: int,
                              comments: str) -> dict:
    """
    Update return comments.
    return_id: Return ID number
    comments: New comment text
    """
    return update_sales_return(return_id, comments)


@tool
def tool_cancel_sales_return(return_id: int) -> dict:
    """
    Cancel a sales return.
    return_id: Return ID number
    """
    return cancel_sales_return(return_id)


@tool
def tool_delete_sales_return(return_id: int) -> dict:
    """
    Delete a sales return.
    return_id: Return ID number
    """
    return delete_sales_return(return_id)


sales_return_tools = [
    tool_create_sales_return,
    tool_get_sales_return,
    tool_get_all_sales_returns,
    tool_update_sales_return,
    tool_cancel_sales_return,
    tool_delete_sales_return
]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

sales_return_agent = create_react_agent(
    model=llm,
    tools=sales_return_tools,
    prompt="""You are a Sales Return Agent for SAP B1.
    Your job is to manage sales returns.
    You can create, read, update, cancel and delete returns.
    Always confirm actions clearly.
    """
)


def run_sales_return_agent(user_message: str) -> str:
    result = sales_return_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content