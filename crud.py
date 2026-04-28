from sqlalchemy.orm import Session
from models import (
    SalesOrder, SalesOrderLine,
    SalesInvoice, SalesInvoiceLine,
    SalesReturn, SalesReturnLine
)
from schemas import (
    SalesOrderCreate, SalesOrderUpdate,
    SalesInvoiceCreate, SalesInvoiceUpdate,
    SalesReturnCreate, SalesReturnUpdate
)

# ─────────────────────────────────────────────
# 📦 SALES ORDER CRUD
# ─────────────────────────────────────────────

def create_order(db: Session, order: SalesOrderCreate):
    """Create a new sales order"""
    db_order = SalesOrder(
        card_code=order.card_code,
        doc_date=order.doc_date,
        doc_due_date=order.doc_due_date,
        comments=order.comments
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Add order lines
    for line in order.document_lines:
        db_line = SalesOrderLine(
            order_id=db_order.id,
            item_code=line.item_code,
            quantity=line.quantity,
            unit_price=line.unit_price
        )
        db.add(db_line)
    db.commit()
    return db_order


def get_order(db: Session, order_id: int):
    """Get a specific sales order by ID"""
    return db.query(SalesOrder).filter(
        SalesOrder.id == order_id
    ).first()


def get_all_orders(db: Session):
    """Get all sales orders"""
    return db.query(SalesOrder).all()


def update_order(db: Session, order_id: int, 
                  order: SalesOrderUpdate):
    """Update a sales order"""
    db_order = db.query(SalesOrder).filter(
        SalesOrder.id == order_id
    ).first()
    if db_order:
        if order.comments:
            db_order.comments = order.comments
        if order.status:
            db_order.status = order.status
        db.commit()
        db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int):
    """Delete a sales order"""
    db_order = db.query(SalesOrder).filter(
        SalesOrder.id == order_id
    ).first()
    if db_order:
        db.delete(db_order)
        db.commit()
    return {"message": f"Order {order_id} deleted successfully"}


def cancel_order(db: Session, order_id: int):
    """Cancel a sales order"""
    db_order = db.query(SalesOrder).filter(
        SalesOrder.id == order_id
    ).first()
    if db_order:
        db_order.status = "cancelled"
        db.commit()
        db.refresh(db_order)
    return {"message": f"Order {order_id} cancelled successfully"}


def close_order(db: Session, order_id: int):
    """Close a sales order"""
    db_order = db.query(SalesOrder).filter(
        SalesOrder.id == order_id
    ).first()
    if db_order:
        db_order.status = "closed"
        db.commit()
        db.refresh(db_order)
    return {"message": f"Order {order_id} closed successfully"}


# ─────────────────────────────────────────────
# 🧾 SALES INVOICE CRUD
# ─────────────────────────────────────────────

def create_invoice(db: Session, invoice: SalesInvoiceCreate):
    """Create a new sales invoice"""
    db_invoice = SalesInvoice(
        card_code=invoice.card_code,
        comments=invoice.comments
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)

    for line in invoice.document_lines:
        db_line = SalesInvoiceLine(
            invoice_id=db_invoice.id,
            item_code=line.item_code,
            quantity=line.quantity,
            tax_code=line.tax_code,
            unit_price=line.unit_price
        )
        db.add(db_line)
    db.commit()
    return db_invoice


def get_invoice(db: Session, invoice_id: int):
    """Get a specific sales invoice by ID"""
    return db.query(SalesInvoice).filter(
        SalesInvoice.id == invoice_id
    ).first()


def get_all_invoices(db: Session):
    """Get all sales invoices"""
    return db.query(SalesInvoice).all()


def update_invoice(db: Session, invoice_id: int,
                    invoice: SalesInvoiceUpdate):
    """Update a sales invoice"""
    db_invoice = db.query(SalesInvoice).filter(
        SalesInvoice.id == invoice_id
    ).first()
    if db_invoice:
        if invoice.comments:
            db_invoice.comments = invoice.comments
        if invoice.status:
            db_invoice.status = invoice.status
        db.commit()
        db.refresh(db_invoice)
    return db_invoice


def delete_invoice(db: Session, invoice_id: int):
    """Delete a sales invoice"""
    db_invoice = db.query(SalesInvoice).filter(
        SalesInvoice.id == invoice_id
    ).first()
    if db_invoice:
        db.delete(db_invoice)
        db.commit()
    return {"message": f"Invoice {invoice_id} deleted successfully"}


def cancel_invoice(db: Session, invoice_id: int):
    """Cancel a sales invoice"""
    db_invoice = db.query(SalesInvoice).filter(
        SalesInvoice.id == invoice_id
    ).first()
    if db_invoice:
        db_invoice.status = "cancelled"
        db.commit()
        db.refresh(db_invoice)
    return {"message": f"Invoice {invoice_id} cancelled successfully"}


# ─────────────────────────────────────────────
# 🔄 SALES RETURN CRUD
# ─────────────────────────────────────────────

def create_return(db: Session, sales_return: SalesReturnCreate):
    """Create a new sales return"""
    db_return = SalesReturn(
        card_code=sales_return.card_code,
        comments=sales_return.comments
    )
    db.add(db_return)
    db.commit()
    db.refresh(db_return)

    for line in sales_return.document_lines:
        db_line = SalesReturnLine(
            return_id=db_return.id,
            item_code=line.item_code,
            quantity=line.quantity,
            tax_code=line.tax_code,
            unit_price=line.unit_price
        )
        db.add(db_line)
    db.commit()
    return db_return


def get_return(db: Session, return_id: int):
    """Get a specific sales return by ID"""
    return db.query(SalesReturn).filter(
        SalesReturn.id == return_id
    ).first()


def get_all_returns(db: Session):
    """Get all sales returns"""
    return db.query(SalesReturn).all()


def update_return(db: Session, return_id: int,
                   sales_return: SalesReturnUpdate):
    """Update a sales return"""
    db_return = db.query(SalesReturn).filter(
        SalesReturn.id == return_id
    ).first()
    if db_return:
        if sales_return.comments:
            db_return.comments = sales_return.comments
        if sales_return.status:
            db_return.status = sales_return.status
        db.commit()
        db.refresh(db_return)
    return db_return


def delete_return(db: Session, return_id: int):
    """Delete a sales return"""
    db_return = db.query(SalesReturn).filter(
        SalesReturn.id == return_id
    ).first()
    if db_return:
        db.delete(db_return)
        db.commit()
    return {"message": f"Return {return_id} deleted successfully"}


def cancel_return(db: Session, return_id: int):
    """Cancel a sales return"""
    db_return = db.query(SalesReturn).filter(
        SalesReturn.id == return_id
    ).first()
    if db_return:
        db_return.status = "cancelled"
        db.commit()
        db.refresh(db_return)
    return {"message": f"Return {return_id} cancelled successfully"}