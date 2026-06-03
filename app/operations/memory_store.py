# app/operations/memory_store.py
# Handles SHORT TERM and LONG TERM memory
# for the SAP B1 Sales Agent

import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# ─────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────
def _get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


# ─────────────────────────────────────────
# LONG TERM MEMORY — saves to PostgreSQL
# Persists across sessions and browser refresh
# ─────────────────────────────────────────
def save_message(session_id: str, role: str, content: str):
    """
    Save a single message to long term memory.
    role: 'user' or 'assistant'
    """
    try:
        conn = _get_conn()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO conversation_memory
            (session_id, role, content)
            VALUES (%s, %s, %s)
        """, (session_id, role, content[:2000]))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[Memory] Save error: {e}")


def load_long_term_memory(session_id: str,
                           limit: int = 10) -> list:
    """
    Load last N messages from PostgreSQL.
    Used to restore memory after browser refresh.
    """
    try:
        conn = _get_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT role, content, timestamp
            FROM conversation_memory
            WHERE session_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """, (session_id, limit))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Reverse so oldest first
        messages = [
            {"role": row[0], "content": row[1]}
            for row in reversed(rows)
        ]
        return messages
    except Exception as e:
        print(f"[Memory] Load error: {e}")
        return []


def get_all_sessions() -> list:
    """Get all unique session IDs — for Sir's dashboard."""
    try:
        conn = _get_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT DISTINCT session_id,
                   MIN(timestamp) as first_seen,
                   MAX(timestamp) as last_seen,
                   COUNT(*) as message_count
            FROM conversation_memory
            GROUP BY session_id
            ORDER BY last_seen DESC
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [
            {
                "session_id":    row[0],
                "first_seen":    str(row[1]),
                "last_seen":     str(row[2]),
                "message_count": row[3]
            }
            for row in rows
        ]
    except Exception as e:
        print(f"[Memory] Sessions error: {e}")
        return []


def clear_session_memory(session_id: str):
    """Clear all messages for a session."""
    try:
        conn = _get_conn()
        cur  = conn.cursor()
        cur.execute("""
            DELETE FROM conversation_memory
            WHERE session_id = %s
        """, (session_id,))
        conn.commit()
        cur.close()
        conn.close()
        print(f"[Memory] Cleared session: {session_id}")
    except Exception as e:
        print(f"[Memory] Clear error: {e}")


# ─────────────────────────────────────────
# SHORT TERM MEMORY — in session only
# Fast access, kept in Streamlit session_state
# ─────────────────────────────────────────
def build_short_term_context(chat_history: list,
                              max_exchanges: int = 5) -> str:
    """
    Build context string from last N exchanges.
    This goes into every Claude prompt.
    """
    if not chat_history:
        return ""

    # Take last max_exchanges * 2 messages
    recent = chat_history[-(max_exchanges * 2):]

    if not recent:
        return ""

    context_lines = ["\n\nCONVERSATION HISTORY:"]
    for msg in recent:
        role    = msg.get("role", "")
        content = msg.get("content", "")[:300]
        if role == "user":
            context_lines.append(f"User: {content}")
        elif role == "assistant":
            context_lines.append(f"Agent: {content}")

    return "\n".join(context_lines)


def get_memory_stats(session_id: str) -> dict:
    """Get memory statistics for current session."""
    try:
        conn = _get_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT COUNT(*),
                   MIN(timestamp),
                   MAX(timestamp)
            FROM conversation_memory
            WHERE session_id = %s
        """, (session_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return {
            "total_messages": row[0] or 0,
            "first_message":  str(row[1]) if row[1] else None,
            "last_message":   str(row[2]) if row[2] else None
        }
    except Exception as e:
        return {"total_messages": 0}