from sqlalchemy import Column, Integer, String, Date, Text, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from database import Base


# ─────────────────────────────────────────────
# 👤 CUSTOMER MODEL
# ─────────────────────────────────────────────

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    card_code = Column(String(50), unique=True, nullable=False)
    card_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())


# ─────────────────────────────────────────────
# 📦 SALES ORDER MODELS
# ─────────────────────────────────────────────

class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id = Column(Integer, primary_key=True, index=True)
    card_code = Column(String(50), nullable=False)
    doc_date = Column(Date, nullable=False)
    doc_due_date = Column(Date, nullable=False)
    comments = Column(Text)
    status = Column(String(20), default="open")
    created_at = Column(TIMESTAMP, server_default=func.now())


class SalesOrderLine(Base):
    __tablename__ = "sales_order_lines"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("sales_orders.id"))
    item_code = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)


# ─────────────────────────────────────────────
# 🧾 SALES INVOICE MODELS
# ─────────────────────────────────────────────

class SalesInvoice(Base):
    __tablename__ = "sales_invoices"

    id = Column(Integer, primary_key=True, index=True)
    card_code = Column(String(50), nullable=False)
    comments = Column(Text)
    status = Column(String(20), default="open")
    created_at = Column(TIMESTAMP, server_default=func.now())


class SalesInvoiceLine(Base):
    __tablename__ = "sales_invoice_lines"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("sales_invoices.id"))
    item_code = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    tax_code = Column(String(20))
    unit_price = Column(DECIMAL(10, 2), nullable=False)


# ─────────────────────────────────────────────
# 🔄 SALES RETURN MODELS
# ─────────────────────────────────────────────

class SalesReturn(Base):
    __tablename__ = "sales_returns"

    id = Column(Integer, primary_key=True, index=True)
    card_code = Column(String(50), nullable=False)
    comments = Column(Text)
    status = Column(String(20), default="open")
    created_at = Column(TIMESTAMP, server_default=func.now())


class SalesReturnLine(Base):
    __tablename__ = "sales_return_lines"

    id = Column(Integer, primary_key=True, index=True)
    return_id = Column(Integer, ForeignKey("sales_returns.id"))
    item_code = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    tax_code = Column(String(20))
    unit_price = Column(DECIMAL(10, 2), nullable=False)