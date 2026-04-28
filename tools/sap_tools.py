import requests

# ─────────────────────────────────────────────
# 🌍 LIVE RENDER URL
# ─────────────────────────────────────────────
BASE_URL = "https://sap-sales-agent-1.onrender.com"


# ─────────────────────────────────────────────
# 📦 SALES ORDER TOOLS
# ─────────────────────────────────────────────

def create_sales_order(card_code: str, doc_date: str,
                        doc_due_date: str, items: list):
    """Create a new Sales Order"""
    url = f"{BASE_URL}/orders"
    payload = {
        "card_code": card_code,
        "doc_date": doc_date,
        "doc_due_date": doc_due_date,
        "document_lines": items
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_sales_order(order_id: int):
    """Get a specific Sales Order by ID"""
    url = f"{BASE_URL}/orders/{order_id}"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_all_sales_orders():
    """Get all Sales Orders"""
    url = f"{BASE_URL}/orders"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def update_sales_order(order_id: int, comments: str):
    """Update a Sales Order"""
    url = f"{BASE_URL}/orders/{order_id}"
    payload = {"comments": comments}
    try:
        response = requests.patch(url, json=payload)
        return {"message": f"Order {order_id} updated successfully"}
    except Exception as e:
        return {"error": str(e)}


def cancel_sales_order(order_id: int):
    """Cancel a Sales Order"""
    url = f"{BASE_URL}/orders/{order_id}/cancel"
    try:
        response = requests.post(url)
        return {"message": f"Order {order_id} cancelled successfully"}
    except Exception as e:
        return {"error": str(e)}


def close_sales_order(order_id: int):
    """Close a Sales Order"""
    url = f"{BASE_URL}/orders/{order_id}/close"
    try:
        response = requests.post(url)
        return {"message": f"Order {order_id} closed successfully"}
    except Exception as e:
        return {"error": str(e)}


def delete_sales_order(order_id: int):
    """Delete a Sales Order"""
    url = f"{BASE_URL}/orders/{order_id}"
    try:
        response = requests.delete(url)
        return {"message": f"Order {order_id} deleted successfully"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 🧾 SALES INVOICE TOOLS
# ─────────────────────────────────────────────

def create_sales_invoice(card_code: str, items: list):
    """Create a new Sales Invoice"""
    url = f"{BASE_URL}/invoices"
    payload = {
        "card_code": card_code,
        "document_lines": items
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_sales_invoice(invoice_id: int):
    """Get a specific Sales Invoice by ID"""
    url = f"{BASE_URL}/invoices/{invoice_id}"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_all_sales_invoices():
    """Get all Sales Invoices"""
    url = f"{BASE_URL}/invoices"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def update_sales_invoice(invoice_id: int, comments: str):
    """Update a Sales Invoice"""
    url = f"{BASE_URL}/invoices/{invoice_id}"
    payload = {"comments": comments}
    try:
        response = requests.patch(url, json=payload)
        return {"message": f"Invoice {invoice_id} updated successfully"}
    except Exception as e:
        return {"error": str(e)}


def cancel_sales_invoice(invoice_id: int):
    """Cancel a Sales Invoice"""
    url = f"{BASE_URL}/invoices/{invoice_id}/cancel"
    try:
        response = requests.post(url)
        return {"message": f"Invoice {invoice_id} cancelled successfully"}
    except Exception as e:
        return {"error": str(e)}


def delete_sales_invoice(invoice_id: int):
    """Delete a Sales Invoice"""
    url = f"{BASE_URL}/invoices/{invoice_id}"
    try:
        response = requests.delete(url)
        return {"message": f"Invoice {invoice_id} deleted successfully"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 🔄 SALES RETURN TOOLS
# ─────────────────────────────────────────────

def create_sales_return(card_code: str, items: list):
    """Create a new Sales Return"""
    url = f"{BASE_URL}/returns"
    payload = {
        "card_code": card_code,
        "document_lines": items
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_sales_return(return_id: int):
    """Get a specific Sales Return by ID"""
    url = f"{BASE_URL}/returns/{return_id}"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_all_sales_returns():
    """Get all Sales Returns"""
    url = f"{BASE_URL}/returns"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def update_sales_return(return_id: int, comments: str):
    """Update a Sales Return"""
    url = f"{BASE_URL}/returns/{return_id}"
    payload = {"comments": comments}
    try:
        response = requests.patch(url, json=payload)
        return {"message": f"Return {return_id} updated successfully"}
    except Exception as e:
        return {"error": str(e)}


def cancel_sales_return(return_id: int):
    """Cancel a Sales Return"""
    url = f"{BASE_URL}/returns/{return_id}/cancel"
    try:
        response = requests.post(url)
        return {"message": f"Return {return_id} cancelled successfully"}
    except Exception as e:
        return {"error": str(e)}


def delete_sales_return(return_id: int):
    """Delete a Sales Return"""
    url = f"{BASE_URL}/returns/{return_id}"
    try:
        response = requests.delete(url)
        return {"message": f"Return {return_id} deleted successfully"}
    except Exception as e:
        return {"error": str(e)}