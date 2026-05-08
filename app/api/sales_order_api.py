from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.crud.sales_order_crud import (
    create_order, get_order, get_all_orders,
    update_order, delete_order, cancel_order, close_order
)
from app.schema.sales_order_schema import (
    SalesOrderCreate, SalesOrderUpdate
)

router = APIRouter()


@router.post("/Orders")
def create_sales_order(order: SalesOrderCreate,
                        db: Session = Depends(get_db)):
    return create_order(db=db, order=order)


@router.get("/Orders")
def get_sales_orders(db: Session = Depends(get_db)):
    orders = get_all_orders(db=db)
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


@router.get("/Orders({order_id})")
def get_sales_order(order_id: int,
                     db: Session = Depends(get_db)):
    order = get_order(db=db, order_id=order_id)
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


@router.patch("/Orders({order_id})")
def update_sales_order(order_id: int,
                        order: SalesOrderUpdate,
                        db: Session = Depends(get_db)):
    return update_order(db=db, order_id=order_id,
                         order=order)


@router.delete("/Orders({order_id})")
def delete_sales_order(order_id: int,
                        db: Session = Depends(get_db)):
    return delete_order(db=db, order_id=order_id)


@router.post("/Orders({order_id})/Cancel")
def cancel_sales_order(order_id: int,
                        db: Session = Depends(get_db)):
    return cancel_order(db=db, order_id=order_id)


@router.post("/Orders({order_id})/Close")
def close_sales_order(order_id: int,
                       db: Session = Depends(get_db)):
    return close_order(db=db, order_id=order_id)