from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine
import models
import crud
from schemas import (
    SalesOrderCreate, SalesOrderUpdate, SalesOrderResponse,
    SalesInvoiceCreate, SalesInvoiceUpdate, SalesInvoiceResponse,
    SalesReturnCreate, SalesReturnUpdate, SalesReturnResponse,
    CustomerResponse
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SAP B1 Sales API",
    description="Sales Team API for Techative Pvt Ltd Solutions",
    version="1.0.0"
)


# ─────────────────────────────────────────────
# 🏠 HOME
# ─────────────────────────────────────────────

@app.get("/")
def home():
    return {
        "message": "SAP B1 Sales API is running!",
        "company": "Techative Pvt Ltd Solutions",
        "version": "1.0.0"
    }


# ─────────────────────────────────────────────
# 👤 CUSTOMER ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/customers")
def get_all_customers(db: Session = Depends(get_db)):
    """Get all customers"""
    customers = crud.get_all_customers(db=db)
    return [
        {
            "CardCode": c.card_code,
            "CardName": c.card_name,
            "Phone": c.phone,
            "Email": c.email,
            "Address": c.address
        }
        for c in customers
    ]


@app.get("/customers/{card_code}")
def get_customer(card_code: str, db: Session = Depends(get_db)):
    """Get a specific customer by CardCode"""
    customer = crud.get_customer(db=db, card_code=card_code)
    if not customer:
        raise HTTPException(status_code=404,
                             detail="Customer not found")
    return {
        "CardCode": customer.card_code,
        "CardName": customer.card_name,
        "Phone": customer.phone,
        "Email": customer.email,
        "Address": customer.address
    }


# ─────────────────────────────────────────────
# 📦 SALES ORDER ENDPOINTS
# ─────────────────────────────────────────────

@app.post("/Orders")
def create_order(order: SalesOrderCreate,
                  db: Session = Depends(get_db)):
    """Create a new sales order"""
    return crud.create_order(db=db, order=order)


@app.get("/Orders")
def get_all_orders(db: Session = Depends(get_db)):
    """Get all sales orders"""
    orders = crud.get_all_orders(db=db)
    return [
        {
            "DocEntry": o.id,
            "CardCode": o.card_code,
            "DocDate": o.doc_date,
            "DocDueDate": o.doc_due_date,
            "Comments": o.comments,
            "Status": o.status
        }
        for o in orders
    ]


@app.get("/Orders({order_id})")
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific sales order"""
    order = crud.get_order(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404,
                             detail="Order not found")
    return {
        "DocEntry": order.id,
        "CardCode": order.card_code,
        "DocDate": order.doc_date,
        "DocDueDate": order.doc_due_date,
        "Comments": order.comments,
        "Status": order.status
    }


@app.patch("/Orders({order_id})")
def update_order(order_id: int, order: SalesOrderUpdate,
                  db: Session = Depends(get_db)):
    """Update a sales order"""
    return crud.update_order(db=db, order_id=order_id, order=order)


@app.delete("/Orders({order_id})")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete a sales order"""
    return crud.delete_order(db=db, order_id=order_id)


@app.post("/Orders({order_id})/Cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """Cancel a sales order"""
    return crud.cancel_order(db=db, order_id=order_id)


@app.post("/Orders({order_id})/Close")
def close_order(order_id: int, db: Session = Depends(get_db)):
    """Close a sales order"""
    return crud.close_order(db=db, order_id=order_id)


# ─────────────────────────────────────────────
# 🧾 SALES INVOICE ENDPOINTS
# ─────────────────────────────────────────────

@app.post("/Invoices")
def create_invoice(invoice: SalesInvoiceCreate,
                    db: Session = Depends(get_db)):
    """Create a new sales invoice"""
    return crud.create_invoice(db=db, invoice=invoice)


@app.get("/Invoices")
def get_all_invoices(db: Session = Depends(get_db)):
    """Get all sales invoices"""
    invoices = crud.get_all_invoices(db=db)
    return [
        {
            "DocEntry": i.id,
            "CardCode": i.card_code,
            "Comments": i.comments,
            "Status": i.status
        }
        for i in invoices
    ]


@app.get("/Invoices({invoice_id})")
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Get a specific sales invoice"""
    invoice = crud.get_invoice(db=db, invoice_id=invoice_id)
    if not invoice:
        raise HTTPException(status_code=404,
                             detail="Invoice not found")
    return {
        "DocEntry": invoice.id,
        "CardCode": invoice.card_code,
        "Comments": invoice.comments,
        "Status": invoice.status
    }


@app.patch("/Invoices({invoice_id})")
def update_invoice(invoice_id: int, invoice: SalesInvoiceUpdate,
                    db: Session = Depends(get_db)):
    """Update a sales invoice"""
    return crud.update_invoice(db=db, invoice_id=invoice_id,
                                invoice=invoice)


@app.delete("/Invoices({invoice_id})")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Delete a sales invoice"""
    return crud.delete_invoice(db=db, invoice_id=invoice_id)


@app.post("/Invoices({invoice_id})/Cancel")
def cancel_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Cancel a sales invoice"""
    return crud.cancel_invoice(db=db, invoice_id=invoice_id)


# ─────────────────────────────────────────────
# 🔄 SALES RETURN ENDPOINTS
# ─────────────────────────────────────────────

@app.post("/Returns")
def create_return(sales_return: SalesReturnCreate,
                   db: Session = Depends(get_db)):
    """Create a new sales return"""
    return crud.create_return(db=db, sales_return=sales_return)


@app.get("/Returns")
def get_all_returns(db: Session = Depends(get_db)):
    """Get all sales returns"""
    returns = crud.get_all_returns(db=db)
    return [
        {
            "DocEntry": r.id,
            "CardCode": r.card_code,
            "Comments": r.comments,
            "Status": r.status
        }
        for r in returns
    ]


@app.get("/Returns({return_id})")
def get_return(return_id: int, db: Session = Depends(get_db)):
    """Get a specific sales return"""
    sales_return = crud.get_return(db=db, return_id=return_id)
    if not sales_return:
        raise HTTPException(status_code=404,
                             detail="Return not found")
    return {
        "DocEntry": sales_return.id,
        "CardCode": sales_return.card_code,
        "Comments": sales_return.comments,
        "Status": sales_return.status
    }


@app.patch("/Returns({return_id})")
def update_return(return_id: int, sales_return: SalesReturnUpdate,
                   db: Session = Depends(get_db)):
    """Update a sales return"""
    return crud.update_return(db=db, return_id=return_id,
                               sales_return=sales_return)


@app.delete("/Returns({return_id})")
def delete_return(return_id: int, db: Session = Depends(get_db)):
    """Delete a sales return"""
    return crud.delete_return(db=db, return_id=return_id)


@app.post("/Returns({return_id})/Cancel")
def cancel_return(return_id: int, db: Session = Depends(get_db)):
    """Cancel a sales return"""
    return crud.cancel_return(db=db, return_id=return_id)