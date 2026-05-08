from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.crud.sales_order_crud import (
    create_return, get_return, get_all_returns,
    update_return, delete_return, cancel_return
)
from app.schema.sales_order_schema import (
    SalesReturnCreate, SalesReturnUpdate
)

router = APIRouter()


@router.post("/Returns")
def create_sales_return(sales_return: SalesReturnCreate,
                         db: Session = Depends(get_db)):
    return create_return(db=db, sales_return=sales_return)


@router.get("/Returns")
def get_sales_returns(db: Session = Depends(get_db)):
    returns = get_all_returns(db=db)
    return [
        {
            "DocEntry": r.id,
            "CardCode": r.card_code,
            "Comments": r.comments,
            "Status": r.status
        }
        for r in returns
    ]


@router.get("/Returns({return_id})")
def get_sales_return(return_id: int,
                      db: Session = Depends(get_db)):
    sales_return = get_return(db=db, return_id=return_id)
    if not sales_return:
        raise HTTPException(status_code=404,
                             detail="Return not found")
    return {
        "DocEntry": sales_return.id,
        "CardCode": sales_return.card_code,
        "Comments": sales_return.comments,
        "Status": sales_return.status
    }


@router.patch("/Returns({return_id})")
def update_sales_return(return_id: int,
                         sales_return: SalesReturnUpdate,
                         db: Session = Depends(get_db)):
    return update_return(db=db, return_id=return_id,
                          sales_return=sales_return)


@router.delete("/Returns({return_id})")
def delete_sales_return(return_id: int,
                         db: Session = Depends(get_db)):
    return delete_return(db=db, return_id=return_id)


@router.post("/Returns({return_id})/Cancel")
def cancel_sales_return(return_id: int,
                         db: Session = Depends(get_db)):
    return cancel_return(db=db, return_id=return_id)