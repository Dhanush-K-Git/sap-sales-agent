from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.crud.sales_order_crud import (
    create_invoice, get_invoice, get_all_invoices,
    update_invoice, delete_invoice, cancel_invoice
)
from app.schema.sales_order_schema import (
    SalesInvoiceCreate, SalesInvoiceUpdate
)

router = APIRouter()


@router.post("/Invoices")
def create_sales_invoice(invoice: SalesInvoiceCreate,
                          db: Session = Depends(get_db)):
    return create_invoice(db=db, invoice=invoice)


@router.get("/Invoices")
def get_sales_invoices(db: Session = Depends(get_db)):
    invoices = get_all_invoices(db=db)
    return [
        {
            "DocEntry": i.id,
            "CardCode": i.card_code,
            "Comments": i.comments,
            "Status": i.status
        }
        for i in invoices
    ]


@router.get("/Invoices({invoice_id})")
def get_sales_invoice(invoice_id: int,
                       db: Session = Depends(get_db)):
    invoice = get_invoice(db=db, invoice_id=invoice_id)
    if not invoice:
        raise HTTPException(status_code=404,
                             detail="Invoice not found")
    return {
        "DocEntry": invoice.id,
        "CardCode": invoice.card_code,
        "Comments": invoice.comments,
        "Status": invoice.status
    }


@router.patch("/Invoices({invoice_id})")
def update_sales_invoice(invoice_id: int,
                          invoice: SalesInvoiceUpdate,
                          db: Session = Depends(get_db)):
    return update_invoice(db=db, invoice_id=invoice_id,
                           invoice=invoice)


@router.delete("/Invoices({invoice_id})")
def delete_sales_invoice(invoice_id: int,
                          db: Session = Depends(get_db)):
    return delete_invoice(db=db, invoice_id=invoice_id)


@router.post("/Invoices({invoice_id})/Cancel")
def cancel_sales_invoice(invoice_id: int,
                          db: Session = Depends(get_db)):
    return cancel_invoice(db=db, invoice_id=invoice_id)