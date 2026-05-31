# streamlit_app.py
import streamlit as st
import asyncio
from dotenv import load_dotenv
from app.agents.supervisor_agent import run_supervisor, run_supervisor_with_memory
load_dotenv()

st.set_page_config(
    page_title="SAP B1 Sales Agent",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

st.markdown("""
    <div class="main-header">
        <h1>SAP B1 Sales Agent</h1>
        <p>Built for Techative Pvt Ltd Solutions</p>
    </div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SESSION STATE — stores full conversation
# ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": """Hello! I am your SAP B1 Sales Assistant at Techative Pvt Ltd.

I can help you with:
- Sales Orders   : Create, Update, Cancel, Close
- Sales Invoices : Create, Cancel, Close, Reopen
- Sales Returns  : Create, Cancel, Close, Reopen
- Analytics      : Reports, customer insights, trends

How can I help you today?"""
    })

# Display full chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ─────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────
if prompt := st.chat_input("Ask anything about your sales data..."):

    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # ── STREAMING response — words appear as generated ──
        response_placeholder = st.empty()
        full_response = ""

        with st.spinner("Thinking..."):
            try:
                # ── Pass FULL conversation history for memory ──
                response = asyncio.run(
                    run_supervisor_with_memory(
                        user_message=prompt,
                        chat_history=st.session_state.messages[:-1]
                    )
                )
                full_response = response
                response_placeholder.markdown(full_response)

            except Exception as e:
                full_response = f"Error: {str(e)}"
                response_placeholder.error(full_response)

        # Save to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response
        })

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### Quick Actions")
    st.markdown("#### Sales Orders")

    if st.button("All Orders", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Show me all sales orders"})
        st.rerun()
    if st.button("Open Orders", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Show me all open orders"})
        st.rerun()
    if st.button("Sales Summary", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Give me complete sales summary"})
        st.rerun()

    st.divider()
    st.markdown("#### Validation")
    customer_code = st.text_input("Customer Code", placeholder="e.g. C001")
    if st.button("Validate Customer", use_container_width=True):
        if customer_code:
            st.session_state.messages.append({"role": "user", "content": f"Validate customer {customer_code}"})
            st.rerun()

    st.divider()
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("**Version:** 2.0.0")
    st.markdown("**Company:** Techative Pvt Ltd")