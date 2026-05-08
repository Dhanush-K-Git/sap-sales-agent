from pydantic import BaseModel
from typing import List, Optional
from datetime import date


# ─────────────────────────────────────────────
# 👤 CUSTOMER SCHEMAS
# ─────────────────────────────────────────────
class CustomerResponse(BaseModel):
    id: int
    CardCode: str
    CardName: str
    Phone: Optional[str]
    Email: Optional[str]
    Address: Optional[str]

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# 📦 SALES ORDER SCHEMAS
# ─────────────────────────────────────────────
class SalesOrderLineSchema(BaseModel):
    ItemCode: str
    Quantity: int
    UnitPrice: float

    class Config:
        from_attributes = True


class SalesOrderCreate(BaseModel):
    CardCode: str
    DocDate: date
    DocDueDate: date
    Comments: Optional[str] = None
    DocumentLines: List[SalesOrderLineSchema]


class SalesOrderUpdate(BaseModel):
    Comments: Optional[str] = None
    Status: Optional[str] = None


class SalesOrderResponse(BaseModel):
    id: int
    CardCode: str
    DocDate: date
    DocDueDate: date
    Comments: Optional[str]
    Status: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# 🧾 SALES INVOICE SCHEMAS
# ─────────────────────────────────────────────
class SalesInvoiceLineSchema(BaseModel):
    ItemCode: str
    Quantity: int
    TaxCode: Optional[str] = None
    UnitPrice: float

    class Config:
        from_attributes = True


class SalesInvoiceCreate(BaseModel):
    CardCode: str
    Comments: Optional[str] = None
    DocumentLines: List[SalesInvoiceLineSchema]


class SalesInvoiceUpdate(BaseModel):
    Comments: Optional[str] = None
    Status: Optional[str] = None


class SalesInvoiceResponse(BaseModel):
    id: int
    CardCode: str
    Comments: Optional[str]
    Status: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# 🔄 SALES RETURN SCHEMAS
# ─────────────────────────────────────────────
class SalesReturnLineSchema(BaseModel):
    ItemCode: str
    Quantity: int
    TaxCode: Optional[str] = None
    UnitPrice: float

    class Config:
        from_attributes = True


class SalesReturnCreate(BaseModel):
    CardCode: str
    Comments: Optional[str] = None
    DocumentLines: List[SalesReturnLineSchema]


class SalesReturnUpdate(BaseModel):
    Comments: Optional[str] = None
    Status: Optional[str] = None


class SalesReturnResponse(BaseModel):
    id: int
    CardCode: str
    Comments: Optional[str]
    Status: str

    class Config:
        from_attributes = True