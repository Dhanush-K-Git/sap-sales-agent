import requests
import json

# This is the base URL of SAP B1 Service Layer
# When sir's team tests it, this will point to their real SAP server
BASE_URL = "https://localhost:50000/b1s/v2"

# We need to ignore SSL warnings for local SAP servers
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ─────────────────────────────────────────────
# 🔐 LOGIN TO SAP
# ─────────────────────────────────────────────
def sap_login(username: str, password: str, company_db: str):
    """Login to SAP B1 and get a session cookie"""
    url = f"{BASE_URL}/Login"
    payload = {
        "UserName": username,
        "Password": password,
        "CompanyDB": company_db
    }
    try:
        response = requests.post(url, json=payload, verify=False)
        if response.status_code == 200:
            return response.cookies
        else:
            return None
    except Exception as e:
        return None


# ─────────────────────────────────────────────
# 📦 SALES ORDER TOOLS
# ─────────────────────────────────────────────
def create_sales_order(card_code: str, doc_date: str, 
                        doc_due_date: str, items: list, cookies):
    """Create a new Sales Order in SAP B1"""
    url = f"{BASE_URL}/Orders"
    payload = {
        "CardCode": card_code,
        "DocDate": doc_date,
        "DocDueDate": doc_due_date,
        "DocumentLines": items
    }
    try:
        response = requests.post(url, json=payload, 
                                  cookies=cookies, verify=False)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_sales_order(order_id: int, cookies):
    """Get a specific Sales Order by ID"""
    url = f"{BASE_URL}/Orders({order_id})"
    try:
        response = requests.get(url, cookies=cookies, verify=False)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_all_sales_orders(cookies):
    """Get all Sales Orders"""
    url = f"{BASE_URL}/Orders"
    try:
        response = requests.get(url, cookies=cookies, verify=False)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def update_sales_order(order_id: int, comments: str, cookies):
    """Update a Sales Order"""
    url = f"{BASE_URL}/Orders({order_id})"
    payload = {"Comments": comments}
    try:
        response = requests.patch(url, json=payload, 
                                   cookies=cookies, verify=False)
        return {"message": f"Order {order_id} updated successfully"}
    except Exception as e:
        return {"error": str(e)}


def cancel_sales_order(order_id: int, cookies):
    """Cancel a Sales Order"""
    url = f"{BASE_URL}/Orders({order_id})/Cancel"
    try:
        response = requests.post(url, cookies=cookies, verify=False)
        return {"message": f"Order {order_id} cancelled successfully"}
    except Exception as e:
        return {"error": str(e)}


def close_sales_order(order_id: int, cookies):
    """Close a Sales Order"""
    url = f"{BASE_URL}/Orders({order_id})/Close"
    try:
        response = requests.post(url, cookies=cookies, verify=False)
        return {"message": f"Order {order_id} closed successfully"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 🧾 SALES INVOICE TOOLS
# ─────────────────────────────────────────────
def create_sales_invoice(card_code: str, items: list, cookies):
    """Create a new Sales Invoice in SAP B1"""
    url = f"{BASE_URL}/Invoices"
    payload = {
        "CardCode": card_code,
        "DocumentLines": items
    }
    try:
        response = requests.post(url, json=payload, 
                                  cookies=cookies, verify=False)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_sales_invoice(invoice_id: int, cookies):
    """Get a specific Sales Invoice by ID"""
    url = f"{BASE_URL}/Invoices({invoice_id})"
    try:
        response = requests.get(url, cookies=cookies, verify=False)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_all_sales_invoices(cookies):
    """Get all Sales Invoices"""
    url = f"{BASE_URL}/Invoices"
    try:
        response = requests.get(url, cookies=cookies, verify=False)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def update_sales_invoice(invoice_id: int, comments: str, cookies):
    """Update a Sales Invoice"""
    url = f"{BASE_URL}/Invoices({invoice_id})"
    payload = {"Comments": comments}
    try:
        response = requests.patch(url, json=payload, 
                                   cookies=cookies, verify=False)
        return {"message": f"Invoice {invoice_id} updated successfully"}
    except Exception as e:
        return {"error": str(e)}


def cancel_sales_invoice(invoice_id: int, cookies):
    """Cancel a Sales Invoice"""
    url = f"{BASE_URL}/Invoices({invoice_id})/Cancel"
    try:
        response = requests.post(url, cookies=cookies, verify=False)
        return {"message": f"Invoice {invoice_id} cancelled successfully"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 🔄 SALES RETURN TOOLS
# ─────────────────────────────────────────────
def create_sales_return(card_code: str, items: list, cookies):
    """Create a new Sales Return in SAP B1"""
    url = f"{BASE_URL}/Returns"
    payload = {
        "CardCode": card_code,
        "DocumentLines": items
    }
    try:
        response = requests.post(url, json=payload, 
                                  cookies=cookies, verify=False)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_sales_return(return_id: int, cookies):
    """Get a specific Sales Return by ID"""
    url = f"{BASE_URL}/Returns({return_id})"
    try:
        response = requests.get(url, cookies=cookies, verify=False)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_all_sales_returns(cookies):
    """Get all Sales Returns"""
    url = f"{BASE_URL}/Returns"
    try:
        response = requests.get(url, cookies=cookies, verify=False)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def update_sales_return(return_id: int, comments: str, cookies):
    """Update a Sales Return"""
    url = f"{BASE_URL}/Returns({return_id})"
    payload = {"Comments": comments}
    try:
        response = requests.patch(url, json=payload, 
                                   cookies=cookies, verify=False)
        return {"message": f"Return {return_id} updated successfully"}
    except Exception as e:
        return {"error": str(e)}


def cancel_sales_return(return_id: int, cookies):
    """Cancel a Sales Return"""
    url = f"{BASE_URL}/Returns({return_id})/Cancel"
    try:
        response = requests.post(url, cookies=cookies, verify=False)
        return {"message": f"Return {return_id} cancelled successfully"}
    except Exception as e:
        return {"error": str(e)}