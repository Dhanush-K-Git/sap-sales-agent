from langchain_core.messages import HumanMessage  # ← THIS WAS MISSING
from app.agents.salesorder.create_agent       import run_create_agent
from app.agents.salesorder.update_agent       import run_update_agent
from app.agents.salesorder.cancel_close_agent import run_cancel_close_agent
from app.agents.salesorder.fetch_agent        import run_fetch_agent
from app.agents.salesorder.validation_agent   import run_validation_agent


async def run_sales_order_agent(state: dict) -> dict:
    intent = state.get("intent", "").lower()
    user_query = state["messages"][-1].content

    if intent in ("create", "place", "new"):
        return await run_create_agent(state)
    elif intent in ("update", "modify", "change"):
        res = run_update_agent(user_query)
        return {"messages": [HumanMessage(content=res)]}
    elif intent in ("cancel", "close"):
        res = run_cancel_close_agent(user_query)
        return {"messages": [HumanMessage(content=res)]}
    else:
        res = run_fetch_agent(user_query)
        return {"messages": [HumanMessage(content=res)]}