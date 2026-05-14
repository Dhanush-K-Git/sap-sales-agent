import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

SYSTEM_PROMPT = """You are a SAP B1 Sales Order creation specialist.
Create sales orders for customers C001-C010 with items I001-I005.
Always confirm customer code, item code, and quantity before creating."""

agent = create_react_agent(llm, tools=[])

async def run_create_agent(state: dict) -> dict:
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state.get("messages", [])
    result = await agent.ainvoke({"messages": messages})
    return {"messages": result["messages"]}