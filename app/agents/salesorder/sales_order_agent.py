from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
from app.agents.salesorder.create_agent import run_create_agent
from app.agents.salesorder.update_agent import run_update_agent
from app.agents.salesorder.cancel_close_agent import run_cancel_close_agent
from app.agents.salesorder.fetch_agent import run_fetch_agent
from app.agents.salesorder.validation_agent import (
    run_validation_agent, validation_agent
)

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)


def route_order_message(user_message: str) -> str:
    system_prompt = (
        "You are a Sales Order supervisor. "
        "Route messages to correct sub-agent. "
        "Sub-agents: "
        "'create': Creating new sales orders. "
        "'update': Updating existing orders. "
        "'cancel_close': Cancelling or closing orders. "
        "'fetch': Getting or showing order data. "
        "'validate': Validating customer, credit or stock. "
        "Reply with ONLY one word! "
        "Examples: "
        "Create a new order -> create. "
        "Update order 123 -> update. "
        "Cancel order 456 -> cancel_close. "
        "Close order 789 -> cancel_close. "
        "Show me all orders -> fetch. "
        "Check stock for Laptop -> validate. "
        "Validate customer C001 -> validate. "
        "Check credit for C001 -> validate."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages)
    route = response.content.strip().lower()

    if route not in ["create", "update",
                      "cancel_close", "fetch", "validate"]:
        route = "fetch"

    return route


def run_sales_order_agent(user_message: str) -> str:
    route = route_order_message(user_message)
    print(f"Sales Order Sub-Agent: → {route.upper()}")

    if route == "create":
        return run_create_agent(user_message)
    elif route == "update":
        return run_update_agent(user_message)
    elif route == "cancel_close":
        return run_cancel_close_agent(user_message)
    elif route == "fetch":
        return run_fetch_agent(user_message)
    elif route == "validate":
        message = f"Please validate this: {user_message}"
        result = validation_agent.invoke({
            "messages": [HumanMessage(content=message)]
        })
        return result["messages"][-1].content

    return "Could not process request. Please try again!"