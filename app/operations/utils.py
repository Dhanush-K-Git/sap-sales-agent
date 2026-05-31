import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL    = os.getenv("SAP_BASE_URL", "http://vzone.in:1662")
HANA_API    = os.getenv("HANA_SQL_API_URL", "http://vzone.in:1662/api/GetMethod/GetData")
DATA_SOURCE = os.getenv("DATA_SOURCE", "sap")


def execute_query(sql: str) -> dict:
    if DATA_SOURCE == "sap":
        return _query_via_sap_api(sql)
    else:
        return _query_via_postgres(sql)


def _query_via_sap_api(sql: str) -> dict:
    try:
        print(f"\n[SAP API] {sql[:100]}...")
        response = requests.get(
            HANA_API,
            params={"query": sql},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return {"data": data, "count": len(data)}
            elif isinstance(data, dict):
                rows = data.get("value") or data.get("data") or []
                return {"data": rows, "count": len(rows)}
            return {"data": [], "count": 0}
        else:
            return {"error": f"API {response.status_code}: {response.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def _query_via_postgres(sql: str) -> dict:
    try:
        import psycopg2
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur  = conn.cursor()
        cur.execute(sql)
        columns = [desc[0] for desc in cur.description]
        rows    = cur.fetchall()
        data    = [dict(zip(columns, [str(v) if v is not None else None for v in row])) for row in rows]
        cur.close()
        conn.close()
        return {"data": data, "count": len(data)}
    except Exception as e:
        return {"error": str(e)}