# Save as create_memory_table.py in project root

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS conversation_memory (
        id          SERIAL PRIMARY KEY,
        session_id  VARCHAR(100) NOT NULL,
        role        VARCHAR(20)  NOT NULL,
        content     TEXT         NOT NULL,
        timestamp   TIMESTAMP    DEFAULT NOW()
    )
""")

cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_session_id
    ON conversation_memory(session_id)
""")

conn.commit()
cur.close()
conn.close()
print("Memory table created successfully!")