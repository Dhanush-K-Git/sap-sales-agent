# app/operations/sap_client.py
# All SAP B1 Service Layer API calls go through here

import requests
import os
from dotenv import load_dotenv

load_dotenv()

SAP_BASE_URL = os.getenv("SAP_BASE_URL", "https://localhost:50000/b1s/v2")

# Disable SSL warnings for localhost testing
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def sap_post(endpoint: str, payload: dict) -> dict:
    """Generic POST to SAP B1 Service Layer."""
    try:
        url = f"{SAP_BASE_URL}/{endpoint}"
        response = requests.post(
            url,
            json=payload,
            verify=False,  # for localhost SSL
            timeout=30
        )
        if response.status_code in (200, 201):
            return {"success": True, "data": response.json()}
        return {
            "success": False,
            "status_code": response.status_code,
            "error": response.text
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    
def sap_get(endpoint: str) -> dict:
    """Generic GET request to SAP B1 Service Layer."""
    url = f"{SAP_BASE_URL}/{endpoint}"
    try:
        # verify=False is needed for your localhost testing
        response = requests.get(
            url, 
            verify=False, 
            timeout=30
            # headers=headers  <-- Uncomment this if you have your Session ID headers ready
        )
        
        if response.status_code == 200:
            return {"success": True, "data": response.json().get("value", [])}
        
        return {
            "success": False, 
            "status_code": response.status_code, 
            "error": response.text
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def sap_patch(endpoint: str, payload: dict) -> dict:
    """Generic PATCH to SAP B1 Service Layer."""
    try:
        url = f"{SAP_BASE_URL}/{endpoint}"
        response = requests.patch(
            url,
            json=payload,
            verify=False,
            timeout=30
        )
        if response.status_code in (200, 204):
            return {"success": True, "message": "Updated successfully"}
        return {
            "success": False,
            "status_code": response.status_code,
            "error": response.text
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def sap_action(endpoint: str) -> dict:
    """Generic POST action (Cancel, Close, Reopen)."""
    try:
        url = f"{SAP_BASE_URL}/{endpoint}"
        response = requests.post(
            url,
            verify=False,
            timeout=30
        )
        if response.status_code in (200, 204):
            return {"success": True, "message": f"{endpoint} action successful"}
        return {
            "success": False,
            "status_code": response.status_code,
            "error": response.text
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────
# SALES ORDER ENDPOINTS
# ─────────────────────────────────────────
def create_sales_order(card_code: str, doc_date: str,
                       doc_due_date: str, items: list) -> dict:
    """POST /Orders"""
    payload = {
        "CardCode": card_code,
        "DocDate": doc_date,
        "DocDueDate": doc_due_date,
        "DocumentLines": [
            {
                "ItemCode": item["ItemCode"],
                "Quantity": item["Quantity"],
                "UnitPrice": item["UnitPrice"]
            }
            for item in items
        ]
    }
    return sap_post("Orders", payload)


def update_sales_order(doc_entry: int, comments: str) -> dict:
    """PATCH /Orders({DocEntry})"""
    payload = {"Comments": comments}
    return sap_patch(f"Orders({doc_entry})", payload)


def cancel_sales_order(doc_entry: int) -> dict:
    """POST /Orders({DocEntry})/Cancel"""
    return sap_action(f"Orders({doc_entry})/Cancel")


def close_sales_order(doc_entry: int) -> dict:
    """POST /Orders({DocEntry})/Close"""
    return sap_action(f"Orders({doc_entry})/Close")


# ─────────────────────────────────────────
# SALES INVOICE ENDPOINTS
# ─────────────────────────────────────────
def create_sales_invoice(card_code: str, items: list) -> dict:
    """POST /Invoices"""
    payload = {
        "CardCode": card_code,
        "DocumentLines": [
            {
                "ItemCode": item["ItemCode"],
                "Quantity": item["Quantity"],
                "TaxCode": item.get("TaxCode", "T1"),
                "UnitPrice": item["UnitPrice"]
            }
            for item in items
        ]
    }
    return sap_post("Invoices", payload)


def cancel_sales_invoice(doc_entry: int) -> dict:
    """POST /Invoices({DocEntry})/Cancel"""
    return sap_action(f"Invoices({doc_entry})/Cancel")


def close_sales_invoice(doc_entry: int) -> dict:
    """POST /Invoices({DocEntry})/Close"""
    return sap_action(f"Invoices({doc_entry})/Close")


def reopen_sales_invoice(doc_entry: int) -> dict:
    """POST /Invoices({DocEntry})/Reopen"""
    return sap_action(f"Invoices({doc_entry})/Reopen")


# ─────────────────────────────────────────
# SALES RETURN ENDPOINTS
# ─────────────────────────────────────────
def create_sales_return(card_code: str, items: list) -> dict:
    """POST /Returns"""
    payload = {
        "CardCode": card_code,
        "DocumentLines": [
            {
                "ItemCode": item["ItemCode"],
                "Quantity": item["Quantity"],
                "TaxCode": item.get("TaxCode", "T1"),
                "UnitPrice": item["UnitPrice"]
            }
            for item in items
        ]
    }
    return sap_post("Returns", payload)


def cancel_sales_return(doc_entry: int) -> dict:
    """POST /Returns({DocEntry})/Cancel"""
    return sap_action(f"Returns({doc_entry})/Cancel")


def close_sales_return(doc_entry: int) -> dict:
    """POST /Returns({DocEntry})/Close"""
    return sap_action(f"Returns({doc_entry})/Close")


def reopen_sales_return(doc_entry: int) -> dict:
    """POST /Returns({DocEntry})/Reopen"""
    return sap_action(f"Returns({doc_entry})/Reopen")