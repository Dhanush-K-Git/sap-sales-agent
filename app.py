from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine
import models
import crud
from schemas import (
    SalesOrderCreate, SalesOrderUpdate, SalesOrderResponse,
    SalesInvoiceCreate, SalesInvoiceUpdate, SalesInvoiceResponse,
    SalesReturnCreate, SalesReturnUpdate, SalesReturnResponse
)

# Create all tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="SAP B1 Sales API",
    description="Sales Team API for Techative Pvt Ltd Solutions",
    version="1.0.0"
)


# ─────────────────────────────────────────────
# 📦 SALES ORDER ENDPOINTS
# ─────────────────────────────────────────────

@app.post("/orders", response_model=SalesOrderResponse)
def create_order(order: SalesOrderCreate, 
                  db: Session = Depends(get_db)):
    """Create a new sales order"""
    return crud.create_order(db=db, order=order)


@app.get("/orders", response_model=list[SalesOrderResponse])
def get_all_orders(db: Session = Depends(get_db)):
    """Get all sales orders"""
    return crud.get_all_orders(db=db)


@app.get("/orders/{order_id}", response_model=SalesOrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific sales order"""
    order = crud.get_order(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, 
                             detail="Order not found")
    return order


@app.patch("/orders/{order_id}", response_model=SalesOrderResponse)
def update_order(order_id: int, order: SalesOrderUpdate,
                  db: Session = Depends(get_db)):
    """Update a sales order"""
    return crud.update_order(db=db, order_id=order_id, order=order)


@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete a sales order"""
    return crud.delete_order(db=db, order_id=order_id)


@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """Cancel a sales order"""
    return crud.cancel_order(db=db, order_id=order_id)


@app.post("/orders/{order_id}/close")
def close_order(order_id: int, db: Session = Depends(get_db)):
    """Close a sales order"""
    return crud.close_order(db=db, order_id=order_id)


# ─────────────────────────────────────────────
# 🧾 SALES INVOICE ENDPOINTS
# ─────────────────────────────────────────────

@app.post("/invoices", response_model=SalesInvoiceResponse)
def create_invoice(invoice: SalesInvoiceCreate,
                    db: Session = Depends(get_db)):
    """Create a new sales invoice"""
    return crud.create_invoice(db=db, invoice=invoice)


@app.get("/invoices", response_model=list[SalesInvoiceResponse])
def get_all_invoices(db: Session = Depends(get_db)):
    """Get all sales invoices"""
    return crud.get_all_invoices(db=db)


@app.get("/invoices/{invoice_id}", 
          response_model=SalesInvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Get a specific sales invoice"""
    invoice = crud.get_invoice(db=db, invoice_id=invoice_id)
    if not invoice:
        raise HTTPException(status_code=404,
                             detail="Invoice not found")
    return invoice


@app.patch("/invoices/{invoice_id}",
            response_model=SalesInvoiceResponse)
def update_invoice(invoice_id: int, invoice: SalesInvoiceUpdate,
                    db: Session = Depends(get_db)):
    """Update a sales invoice"""
    return crud.update_invoice(db=db, invoice_id=invoice_id,
                                invoice=invoice)


@app.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Delete a sales invoice"""
    return crud.delete_invoice(db=db, invoice_id=invoice_id)


@app.post("/invoices/{invoice_id}/cancel")
def cancel_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Cancel a sales invoice"""
    return crud.cancel_invoice(db=db, invoice_id=invoice_id)


# ─────────────────────────────────────────────
# 🔄 SALES RETURN ENDPOINTS
# ─────────────────────────────────────────────

@app.post("/returns", response_model=SalesReturnResponse)
def create_return(sales_return: SalesReturnCreate,
                   db: Session = Depends(get_db)):
    """Create a new sales return"""
    return crud.create_return(db=db, sales_return=sales_return)


@app.get("/returns", response_model=list[SalesReturnResponse])
def get_all_returns(db: Session = Depends(get_db)):
    """Get all sales returns"""
    return crud.get_all_returns(db=db)


@app.get("/returns/{return_id}",
          response_model=SalesReturnResponse)
def get_return(return_id: int, db: Session = Depends(get_db)):
    """Get a specific sales return"""
    sales_return = crud.get_return(db=db, return_id=return_id)
    if not sales_return:
        raise HTTPException(status_code=404,
                             detail="Return not found")
    return sales_return


@app.patch("/returns/{return_id}",
            response_model=SalesReturnResponse)
def update_return(return_id: int, sales_return: SalesReturnUpdate,
                   db: Session = Depends(get_db)):
    """Update a sales return"""
    return crud.update_return(db=db, return_id=return_id,
                               sales_return=sales_return)


@app.delete("/returns/{return_id}")
def delete_return(return_id: int, db: Session = Depends(get_db)):
    """Delete a sales return"""
    return crud.delete_return(db=db, return_id=return_id)


@app.post("/returns/{return_id}/cancel")
def cancel_return(return_id: int, db: Session = Depends(get_db)):
    """Cancel a sales return"""
    return crud.cancel_return(db=db, return_id=return_id)


# ─────────────────────────────────────────────
# 🏠 HOME ENDPOINT
# ─────────────────────────────────────────────

@app.get("/")
def home():
    return {
        "message": "SAP B1 Sales API is running!",
        "company": "Techative Pvt Ltd Solutions",
        "version": "1.0.0"
    }