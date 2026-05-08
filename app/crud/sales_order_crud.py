from sqlalchemy.orm import Session
from app.model.sales_order_model import (
    Customer,
    SalesOrder, SalesOrderLine,
    SalesInvoice, SalesInvoiceLine,
    SalesReturn, SalesReturnLine
)
from app.schema.sales_order_schema import (
    SalesOrderCreate, SalesOrderUpdate,
    SalesInvoiceCreate, SalesInvoiceUpdate,
    SalesReturnCreate, SalesReturnUpdate
)


# ─────────────────────────────────────────────
# 👤 CUSTOMER CRUD
# ─────────────────────────────────────────────
def get_all_customers(db: Session):
    return db.query(Customer).all()


def get_customer(db: Session, card_code: str):
    return db.query(Customer).filter(
        Customer.card_code == card_code
    ).first()


# ─────────────────────────────────────────────
# 📦 SALES ORDER CRUD
# ─────────────────────────────────────────────
def create_order(db: Session, order: SalesOrderCreate):
    db_order = SalesOrder(
        card_code=order.CardCode,
        doc_date=order.DocDate,
        doc_due_date=order.DocDueDate,
        comments=order.Comments
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for line in order.DocumentLines:
        db_line = SalesOrderLine(
            order_id=db_order.id,
            item_code=line.ItemCode,
            quantity=line.Quantity,
            unit_price=line.UnitPrice
        )
        db.add(db_line)
    db.commit()
    return db_order


def get_order(db: Session, order_id: int):
    return db.query(SalesOrder).filter(
        SalesOrder.id == order_id
    ).first()


def get_all_orders(db: Session):
    return db.query(SalesOrder).all()


def update_order(db: Session, order_id: int,
                  order: SalesOrderUpdate):
    db_order = db.query(SalesOrder).filter(
        SalesOrder.id == order_id
    ).first()
    if db_order:
        if order.Comments:
            db_order.comments = order.Comments
        if order.Status:
            db_order.status = order.Status
        db.commit()
        db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int):
    db_order = db.query(SalesOrder).filter(
        SalesOrder.id == order_id
    ).first()
    if db_order:
        db.delete(db_order)
        db.commit()
    return {"message": f"Order {order_id} deleted!"}


def cancel_order(db: Session, order_id: int):
    db_order = db.query(SalesOrder).filter(
        SalesOrder.id == order_id
    ).first()
    if db_order:
        db_order.status = "cancelled"
        db.commit()
        db.refresh(db_order)
    return {"message": f"Order {order_id} cancelled!"}


def close_order(db: Session, order_id: int):
    db_order = db.query(SalesOrder).filter(
        SalesOrder.id == order_id
    ).first()
    if db_order:
        db_order.status = "closed"
        db.commit()
        db.refresh(db_order)
    return {"message": f"Order {order_id} closed!"}


# ─────────────────────────────────────────────
# 🧾 SALES INVOICE CRUD
# ─────────────────────────────────────────────
def create_invoice(db: Session,
                    invoice: SalesInvoiceCreate):
    db_invoice = SalesInvoice(
        card_code=invoice.CardCode,
        comments=invoice.Comments
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)

    for line in invoice.DocumentLines:
        db_line = SalesInvoiceLine(
            invoice_id=db_invoice.id,
            item_code=line.ItemCode,
            quantity=line.Quantity,
            tax_code=line.TaxCode,
            unit_price=line.UnitPrice
        )
        db.add(db_line)
    db.commit()
    return db_invoice


def get_invoice(db: Session, invoice_id: int):
    return db.query(SalesInvoice).filter(
        SalesInvoice.id == invoice_id
    ).first()


def get_all_invoices(db: Session):
    return db.query(SalesInvoice).all()


def update_invoice(db: Session, invoice_id: int,
                    invoice: SalesInvoiceUpdate):
    db_invoice = db.query(SalesInvoice).filter(
        SalesInvoice.id == invoice_id
    ).first()
    if db_invoice:
        if invoice.Comments:
            db_invoice.comments = invoice.Comments
        if invoice.Status:
            db_invoice.status = invoice.Status
        db.commit()
        db.refresh(db_invoice)
    return db_invoice


def delete_invoice(db: Session, invoice_id: int):
    db_invoice = db.query(SalesInvoice).filter(
        SalesInvoice.id == invoice_id
    ).first()
    if db_invoice:
        db.delete(db_invoice)
        db.commit()
    return {"message": f"Invoice {invoice_id} deleted!"}


def cancel_invoice(db: Session, invoice_id: int):
    db_invoice = db.query(SalesInvoice).filter(
        SalesInvoice.id == invoice_id
    ).first()
    if db_invoice:
        db_invoice.status = "cancelled"
        db.commit()
        db.refresh(db_invoice)
    return {"message": f"Invoice {invoice_id} cancelled!"}


# ─────────────────────────────────────────────
# 🔄 SALES RETURN CRUD
# ─────────────────────────────────────────────
def create_return(db: Session,
                   sales_return: SalesReturnCreate):
    db_return = SalesReturn(
        card_code=sales_return.CardCode,
        comments=sales_return.Comments
    )
    db.add(db_return)
    db.commit()
    db.refresh(db_return)

    for line in sales_return.DocumentLines:
        db_line = SalesReturnLine(
            return_id=db_return.id,
            item_code=line.ItemCode,
            quantity=line.Quantity,
            tax_code=line.TaxCode,
            unit_price=line.UnitPrice
        )
        db.add(db_line)
    db.commit()
    return db_return


def get_return(db: Session, return_id: int):
    return db.query(SalesReturn).filter(
        SalesReturn.id == return_id
    ).first()


def get_all_returns(db: Session):
    return db.query(SalesReturn).all()


def update_return(db: Session, return_id: int,
                   sales_return: SalesReturnUpdate):
    db_return = db.query(SalesReturn).filter(
        SalesReturn.id == return_id
    ).first()
    if db_return:
        if sales_return.Comments:
            db_return.comments = sales_return.Comments
        if sales_return.Status:
            db_return.status = sales_return.Status
        db.commit()
        db.refresh(db_return)
    return db_return


def delete_return(db: Session, return_id: int):
    db_return = db.query(SalesReturn).filter(
        SalesReturn.id == return_id
    ).first()
    if db_return:
        db.delete(db_return)
        db.commit()
    return {"message": f"Return {return_id} deleted!"}


def cancel_return(db: Session, return_id: int):
    db_return = db.query(SalesReturn).filter(
        SalesReturn.id == return_id
    ).first()
    if db_return:
        db_return.status = "cancelled"
        db.commit()
        db.refresh(db_return)
    return {"message": f"Return {return_id} cancelled!"}