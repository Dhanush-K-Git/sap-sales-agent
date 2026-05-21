# app/agents/salesorder/sales_order_agent.py
from app.agents.salesorder.create_agent       import run_create_agent
from app.agents.salesorder.update_agent       import run_update_agent
from app.agents.salesorder.cancel_close_agent import run_cancel_close_agent
from app.agents.salesorder.fetch_agent        import run_fetch_agent
from app.agents.salesorder.validation_agent   import run_validation_agent


def run_sales_order_agent(user_message: str) -> str:
    """Route to correct sales order sub-agent based on keywords."""
    msg = user_message.lower()

    if any(w in msg for w in ["create", "place", "new order", "make"]):
        return run_create_agent(user_message)
    elif any(w in msg for w in ["update", "modify", "change", "edit"]):
        return run_update_agent(user_message)
    elif any(w in msg for w in ["cancel", "close"]):
        return run_cancel_close_agent(user_message)
    elif any(w in msg for w in ["validate", "check customer", "check stock"]):
        return run_validation_agent(user_message)
    else:
        return run_fetch_agent(user_message)