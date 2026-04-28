from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# ─────────────────────────────────────────────
# 📦 SALES ORDER SCHEMAS
# ─────────────────────────────────────────────

class SalesOrderLineSchema(BaseModel):
    item_code: str
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class SalesOrderCreate(BaseModel):
    card_code: str
    doc_date: date
    doc_due_date: date
    comments: Optional[str] = None
    document_lines: List[SalesOrderLineSchema]


class SalesOrderUpdate(BaseModel):
    comments: Optional[str] = None
    status: Optional[str] = None


class SalesOrderResponse(BaseModel):
    id: int
    card_code: str
    doc_date: date
    doc_due_date: date
    comments: Optional[str]
    status: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# 🧾 SALES INVOICE SCHEMAS
# ─────────────────────────────────────────────

class SalesInvoiceLineSchema(BaseModel):
    item_code: str
    quantity: int
    tax_code: Optional[str] = None
    unit_price: float

    class Config:
        from_attributes = True


class SalesInvoiceCreate(BaseModel):
    card_code: str
    comments: Optional[str] = None
    document_lines: List[SalesInvoiceLineSchema]


class SalesInvoiceUpdate(BaseModel):
    comments: Optional[str] = None
    status: Optional[str] = None


class SalesInvoiceResponse(BaseModel):
    id: int
    card_code: str
    comments: Optional[str]
    status: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# 🔄 SALES RETURN SCHEMAS
# ─────────────────────────────────────────────

class SalesReturnLineSchema(BaseModel):
    item_code: str
    quantity: int
    tax_code: Optional[str] = None
    unit_price: float

    class Config:
        from_attributes = True


class SalesReturnCreate(BaseModel):
    card_code: str
    comments: Optional[str] = None
    document_lines: List[SalesReturnLineSchema]


class SalesReturnUpdate(BaseModel):
    comments: Optional[str] = None
    status: Optional[str] = None


class SalesReturnResponse(BaseModel):
    id: int
    card_code: str
    comments: Optional[str]
    status: str

    class Config:
        from_attributes = True