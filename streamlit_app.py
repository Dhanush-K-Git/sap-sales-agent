# streamlit_app.py
import streamlit as st
import asyncio
import uuid
from dotenv import load_dotenv
from app.agents.supervisor_agent import run_supervisor_with_memory
from app.operations.memory_store import (
    save_message,
    load_long_term_memory,
    clear_session_memory,
    get_memory_stats
)

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
    .memory-badge {
        background: #1e3c72;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        display: inline-block;
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
# SESSION ID — unique per browser session
# Used as key for long term memory
# ─────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
    print(f"[Memory] New session: {st.session_state.session_id}")

# ─────────────────────────────────────────
# SHORT TERM — load from session_state
# LONG TERM  — restore from PostgreSQL
#              if session_state is empty
# ─────────────────────────────────────────
if "messages" not in st.session_state:
    # Try to restore from long term memory
    restored = load_long_term_memory(
        st.session_state.session_id,
        limit=10
    )

    if restored:
        # Long term memory found — restore it
        st.session_state.messages = restored
        print(f"[Memory] Restored {len(restored)} messages")
    else:
        # Fresh session — show welcome message
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

# ─────────────────────────────────────────
# DISPLAY CHAT HISTORY
# ─────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ─────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────
if prompt := st.chat_input("Ask anything about your sales data..."):

    # 1 — Add to short term (session_state)
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # 2 — Save to long term (PostgreSQL)
    save_message(
        session_id=st.session_state.session_id,
        role="user",
        content=prompt
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # 3 — Pass short term history to agent
                response = asyncio.run(
                    run_supervisor_with_memory(
                        user_message=prompt,
                        chat_history=st.session_state.messages[:-1]
                    )
                )

                st.markdown(response)

                # 4 — Save response to short term
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

                # 5 — Save response to long term
                save_message(
                    session_id=st.session_state.session_id,
                    role="assistant",
                    content=response
                )

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)


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

    # ── MEMORY STATUS ──────────────────────
    st.markdown("#### Memory Status")
    stats = get_memory_stats(st.session_state.session_id)

    st.markdown(f"""
    <div class="memory-badge">Session: {st.session_state.session_id}</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    **Short term:** {len(st.session_state.messages)} messages in session
    **Long term:** {stats['total_messages']} messages in database
    """)

    if stats['last_message']:
        st.caption(f"Last active: {stats['last_message'][:16]}")

    st.divider()

    # ── CLEAR BUTTONS ──────────────────────
    if st.button("Clear Chat (keep memory)", use_container_width=True):
        # Only clear screen — keep long term
        st.session_state.messages = []
        st.rerun()

    if st.button("Clear All Memory", use_container_width=True):
        # Clear both short and long term
        st.session_state.messages = []
        clear_session_memory(st.session_state.session_id)
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.rerun()

    st.divider()
    st.markdown("**Version:** 2.0.0")
    st.markdown("**Company:** Techative Pvt Ltd")