import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# 🌍 BASE URL
# ─────────────────────────────────────────────
BASE_URL = "https://sap-sales-agent-1.onrender.com"


# ─────────────────────────────────────────────
# 📦 SALES ORDER UTILS
# ─────────────────────────────────────────────
def create_sales_order(card_code: str, doc_date: str,
                        doc_due_date: str, items: list):
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
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_sales_order(order_id: int):
    url = f"{BASE_URL}/Orders({order_id})"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_all_sales_orders():
    url = f"{BASE_URL}/Orders"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def update_sales_order(order_id: int, comments: str):
    url = f"{BASE_URL}/Orders({order_id})"
    payload = {"Comments": comments}
    try:
        response = requests.patch(url, json=payload)
        return {"message": f"Order {order_id} updated!"}
    except Exception as e:
        return {"error": str(e)}


def cancel_sales_order(order_id: int):
    url = f"{BASE_URL}/Orders({order_id})/Cancel"
    try:
        response = requests.post(url)
        return {"message": f"Order {order_id} cancelled!"}
    except Exception as e:
        return {"error": str(e)}


def close_sales_order(order_id: int):
    url = f"{BASE_URL}/Orders({order_id})/Close"
    try:
        response = requests.post(url)
        return {"message": f"Order {order_id} closed!"}
    except Exception as e:
        return {"error": str(e)}


def delete_sales_order(order_id: int):
    url = f"{BASE_URL}/Orders({order_id})"
    try:
        response = requests.delete(url)
        return {"message": f"Order {order_id} deleted!"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 🧾 SALES INVOICE UTILS
# ─────────────────────────────────────────────
def create_sales_invoice(card_code: str, items: list):
    url = f"{BASE_URL}/Invoices"
    payload = {
        "CardCode": card_code,
        "DocumentLines": [
            {
                "ItemCode": item.get("ItemCode") or item.get("item_code"),
                "Quantity": item.get("Quantity") or item.get("quantity"),
                "TaxCode": item.get("TaxCode") or item.get("tax_code"),
                "UnitPrice": item.get("UnitPrice") or item.get("unit_price")
            }
            for item in items
        ]
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_sales_invoice(invoice_id: int):
    url = f"{BASE_URL}/Invoices({invoice_id})"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_all_sales_invoices():
    url = f"{BASE_URL}/Invoices"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def update_sales_invoice(invoice_id: int, comments: str):
    url = f"{BASE_URL}/Invoices({invoice_id})"
    payload = {"Comments": comments}
    try:
        response = requests.patch(url, json=payload)
        return {"message": f"Invoice {invoice_id} updated!"}
    except Exception as e:
        return {"error": str(e)}


def cancel_sales_invoice(invoice_id: int):
    url = f"{BASE_URL}/Invoices({invoice_id})/Cancel"
    try:
        response = requests.post(url)
        return {"message": f"Invoice {invoice_id} cancelled!"}
    except Exception as e:
        return {"error": str(e)}


def delete_sales_invoice(invoice_id: int):
    url = f"{BASE_URL}/Invoices({invoice_id})"
    try:
        response = requests.delete(url)
        return {"message": f"Invoice {invoice_id} deleted!"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 🔄 SALES RETURN UTILS
# ─────────────────────────────────────────────
def create_sales_return(card_code: str, items: list):
    url = f"{BASE_URL}/Returns"
    payload = {
        "CardCode": card_code,
        "DocumentLines": [
            {
                "ItemCode": item.get("ItemCode") or item.get("item_code"),
                "Quantity": item.get("Quantity") or item.get("quantity"),
                "TaxCode": item.get("TaxCode") or item.get("tax_code"),
                "UnitPrice": item.get("UnitPrice") or item.get("unit_price")
            }
            for item in items
        ]
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_sales_return(return_id: int):
    url = f"{BASE_URL}/Returns({return_id})"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_all_sales_returns():
    url = f"{BASE_URL}/Returns"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def update_sales_return(return_id: int, comments: str):
    url = f"{BASE_URL}/Returns({return_id})"
    payload = {"Comments": comments}
    try:
        response = requests.patch(url, json=payload)
        return {"message": f"Return {return_id} updated!"}
    except Exception as e:
        return {"error": str(e)}


def cancel_sales_return(return_id: int):
    url = f"{BASE_URL}/Returns({return_id})/Cancel"
    try:
        response = requests.post(url)
        return {"message": f"Return {return_id} cancelled!"}
    except Exception as e:
        return {"error": str(e)}


def delete_sales_return(return_id: int):
    url = f"{BASE_URL}/Returns({return_id})"
    try:
        response = requests.delete(url)
        return {"message": f"Return {return_id} deleted!"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 🔍 QUERY UTILS
# ─────────────────────────────────────────────
def execute_query(sql: str):
    """Execute SQL query via API"""
    try:
        response = requests.get(
            f"{BASE_URL}/query",
            params={"sql": sql}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}