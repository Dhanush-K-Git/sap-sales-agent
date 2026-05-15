import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
print(f"DB URL found: {bool(db_url)}")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Test 1: Check OCRD table (customers)
    cur.execute('SELECT COUNT(*) FROM "OCRD"')
    print(f"Customers in OCRD: {cur.fetchone()[0]}")

    # Test 2: Check ORDR table (orders)
    cur.execute('SELECT COUNT(*) FROM "ORDR"')
    print(f"Orders in ORDR: {cur.fetchone()[0]}")

    # Test 3: List all tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cur.fetchall()
    print(f"\nAll tables in DB:")
    for t in tables:
        print(f"  - {t[0]}")

    cur.close()
    conn.close()
    print("\nDB connection OK!")

except Exception as e:
    print(f"DB ERROR: {e}")
    