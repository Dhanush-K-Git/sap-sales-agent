import streamlit as st
import asyncio
from dotenv import load_dotenv
from app.agents.supervisor_agent import run_supervisor

load_dotenv()

# PAGE CONFIG
st.set_page_config(
    page_title="SAP B1 Sales Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72, #2a69ac);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("""
    <div class="main-header">
        <h1>🤖 SAP B1 Sales Team Agent</h1>
        <p>Built for Techative Pvt Ltd Solutions</p>
    </div>
""", unsafe_allow_html=True)

# CHAT INIT
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": """👋 Hello! I'm **Alex**, your SAP B1 Sales Assistant!

I can help you with:
- 📦 **Sales Orders** - Create, update, cancel, close
- 🧾 **Sales Invoices** - Create, update, cancel
- 🔄 **Sales Returns** - Create, update, cancel
- 🔍 **Analytics** - Reports, trends, insights
- ✅ **Validation** - Check customers, stock, credit

How can I help you today? 😊"""
    })

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ✅ FIX: The ENTIRE response block must be INSIDE this if statement
if prompt := st.chat_input("Ask me anything about your sales data..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ✅ This block is correctly indented inside the if
    with st.chat_message("assistant"):
        with st.spinner("Alex is thinking... 🤔"):
            try:
                response = asyncio.run(run_supervisor(prompt))
                st.markdown(response)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
            except Exception as e:
                error_msg = f"⚠️ Error: {str(e)}"
                st.error(error_msg)

# SIDEBAR
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/SAP_2011_logo.svg/1200px-SAP_2011_logo.svg.png",
        width=100
    )
    st.markdown("### 🚀 Quick Actions")

    st.markdown("#### 📦 Sales Orders")
    if st.button("📋 All Orders", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Show me all sales orders"})
        st.rerun()

    if st.button("✅ Open Orders", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Show me all open orders"})
        st.rerun()

    if st.button("📊 Sales Summary", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Give me a complete sales summary"})
        st.rerun()

    st.divider()
    st.markdown("#### ✅ Quick Validation")
    customer_code = st.text_input("Customer Code", placeholder="e.g. C001")
    if st.button("Validate Customer", use_container_width=True):
        if customer_code:
            st.session_state.messages.append({"role": "user", "content": f"Validate customer {customer_code}"})
            st.rerun()

    item_name = st.text_input("Item Name", placeholder="e.g. Laptop")
    if st.button("Check Stock", use_container_width=True):
        if item_name:
            st.session_state.messages.append({"role": "user", "content": f"What is the stock for {item_name}?"})
            st.rerun()

    st.divider()
    st.markdown("#### 🔍 Analytics")
    if st.button("💰 Top Customers", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Which customers have highest order values?"})
        st.rerun()

    if st.button("📦 Popular Items", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Which items are ordered the most?"})
        st.rerun()

    if st.button("📅 Monthly Orders", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Show me orders grouped by month"})
        st.rerun()

    st.divider()
    st.markdown("#### ℹ️ System Info")
    st.markdown("**API:** [Open Docs](https://sap-sales-agent-1.onrender.com/docs)")
    st.markdown("**Version:** 1.0.0")
    st.markdown("**Company:** Techative Pvt Ltd")

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()