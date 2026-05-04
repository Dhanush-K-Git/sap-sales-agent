from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import os
import requests
from dotenv import load_dotenv
from agents.validation_agent import run_validation_agent

load_dotenv()

BASE_URL = "https://sap-sales-agent-1.onrender.com"


# ─────────────────────────────────────────────
# 🔧 CREATE TOOLS
# ─────────────────────────────────────────────

@tool
def create_order_with_validation(
        card_code: str,
        doc_date: str,
        doc_due_date: str,
        items: list,
        order_total: float) -> dict:
    """
    Create a sales order with full validation.
    card_code: Customer code e.g C001
    doc_date: Order date e.g 2026-04-28
    doc_due_date: Due date e.g 2026-04-30
    items: List of items with ItemCode, Quantity, UnitPrice
    order_total: Total amount of the order
    """
    try:
        # Step 1 — Run Validations
        validation_result = run_validation_agent(
            card_code=card_code,
            order_total=order_total,
            items=items
        )

        warnings = []
        if "warnings" in str(validation_result):
            warnings = validation_result.get("warnings", [])

        # Step 2 — Create Order regardless
        url = f"{BASE_URL}/Orders"
        payload = {
            "CardCode": card_code,
            "DocDate": doc_date,
            "DocDueDate": doc_due_date,
            "DocumentLines": [
                {
                    "ItemCode": item.get("ItemCode") or item.get("item_code"),
                    "Quantity": item.get("Quantity") or item.get("quantity"),
                    "UnitPrice": item.get("UnitPrice") or item.get("unit_price")
                }
                for item in items
            ]
        }
        response = requests.post(url, json=payload)
        order_data = response.json()

        return {
            "success": True,
            "order": order_data,
            "warnings": warnings,
            "validation_summary": validation_result["response"]
        }

    except Exception as e:
        return {"error": str(e)}


@tool
def extract_order_details(user_message: str) -> dict:
    """
    Extract order details from user message.
    user_message: The user's message about creating an order
    """
    return {
        "message": user_message,
        "instruction": """
        Extract these details:
        - CardCode (customer code)
        - DocDate (order date)
        - DocDueDate (due date)
        - Items (list of items with ItemCode, Quantity, UnitPrice)
        - OrderTotal (sum of all line totals)
        """
    }


# ─────────────────────────────────────────────
# 🤖 BUILD CREATE AGENT
# ─────────────────────────────────────────────

create_tools = [
    create_order_with_validation,
    extract_order_details
]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

create_agent = create_react_agent(
    model=llm,
    tools=create_tools,
    prompt="""You are a Create Agent for SAP Business One.
    Your job is to create sales orders.

    WORKFLOW:
    1. Extract order details from user message
    2. Calculate order total (quantity × price for each item)
    3. Call create_order_with_validation with all details
    4. Show any warnings to user
    5. Confirm order creation with Order ID

    IMPORTANT RULES:
    - Always extract ALL details before creating
    - Always calculate order total
    - Always show validation warnings if any
    - Always confirm with order details after creation
    - Never skip validation

    Example:
    User: "Create order for C001, item I001, qty 2, price 1500"
    You: Extract details → Validate → Create → Confirm
    """
)


def run_create_agent(user_message: str) -> str:
    """Run the create agent"""
    result = create_agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return result["messages"][-1].content