from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.base import get_db, engine
from app.model import sales_order_model
from app.api.sales_order_api import router as order_router
from app.api.sales_invoice_api import router as invoice_router
from app.api.sales_return_api import router as return_router

# Create all tables
sales_order_model.Base.metadata.create_all(bind=engine)


# ─────────────────────────────────────────────
# 🗄️ SETUP SAP TABLES AND DATA
# ─────────────────────────────────────────────
def setup_sap_tables():
    db = next(get_db())
    try:
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS "OCRD" (
                "CardCode" VARCHAR(50) PRIMARY KEY,
                "CardName" VARCHAR(100) NOT NULL,
                "Phone" VARCHAR(20),
                "Email" VARCHAR(100),
                "Address" TEXT,
                "CreditLimit" DECIMAL(10,2) DEFAULT 0.00,
                "Balance" DECIMAL(10,2) DEFAULT 0.00
            )
        """))
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS "OITM" (
                "ItemCode" VARCHAR(50) PRIMARY KEY,
                "ItemName" VARCHAR(100) NOT NULL,
                "Price" DECIMAL(10,2) NOT NULL,
                "Stock" DECIMAL(10,2) DEFAULT 0.00,
                "ItemGroup" VARCHAR(50)
            )
        """))
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS "ORDR" (
                "DocEntry" SERIAL PRIMARY KEY,
                "DocNum" INTEGER UNIQUE NOT NULL,
                "DocDate" DATE NOT NULL,
                "DocDueDate" DATE NOT NULL,
                "CardCode" VARCHAR(50),
                "CardName" VARCHAR(100) NOT NULL,
                "DocTotal" DECIMAL(10,2) NOT NULL,
                "DocStatus" VARCHAR(20) DEFAULT 'O',
                "Comments" TEXT
            )
        """))
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS "RDR1" (
                "LineNum" SERIAL PRIMARY KEY,
                "DocEntry" INTEGER REFERENCES "ORDR"("DocEntry"),
                "ItemCode" VARCHAR(50),
                "ItemName" VARCHAR(100) NOT NULL,
                "Quantity" DECIMAL(10,2) NOT NULL,
                "Price" DECIMAL(10,2) NOT NULL,
                "LineTotal" DECIMAL(10,2) NOT NULL
            )
        """))
        db.commit()
        print("✅ SAP tables created!")

        # Clear and reload data
        db.execute(text('DELETE FROM "RDR1"'))
        db.execute(text('DELETE FROM "ORDR"'))
        db.execute(text('DELETE FROM "OITM"'))
        db.execute(text('DELETE FROM "OCRD"'))
        db.commit()

        db.execute(text("""
            INSERT INTO "OCRD"
            ("CardCode","CardName","Phone","Email",
             "Address","CreditLimit","Balance")
            VALUES
            ('C001','Rahul Sharma','9876543210',
             'rahul@email.com','Bangalore, Karnataka',
             50000.00,15000.00),
            ('C002','Priya Singh','9845678901',
             'priya@email.com','Mumbai, Maharashtra',
             75000.00,20000.00),
            ('C003','Amit Kumar','9756432109',
             'amit@email.com','Delhi, NCR',
             30000.00,5000.00),
            ('C004','Sneha Patel','9654321098',
             'sneha@email.com','Ahmedabad, Gujarat',
             60000.00,25000.00),
            ('C005','Vikram Nair','9543210987',
             'vikram@email.com','Chennai, Tamil Nadu',
             45000.00,10000.00),
            ('C006','Deepa Reddy','9432109876',
             'deepa@email.com','Hyderabad, Telangana',
             55000.00,18000.00),
            ('C007','Suresh Kumar','9321098765',
             'suresh@email.com','Pune, Maharashtra',
             40000.00,8000.00),
            ('C008','Anita Desai','9210987654',
             'anita@email.com','Surat, Gujarat',
             65000.00,22000.00),
            ('C009','Rajesh Verma','9109876543',
             'rajesh@email.com','Jaipur, Rajasthan',
             35000.00,12000.00),
            ('C010','Meena Iyer','9098765432',
             'meena@email.com','Kochi, Kerala',
             70000.00,30000.00)
        """))

        db.execute(text("""
            INSERT INTO "OITM"
            ("ItemCode","ItemName","Price","Stock","ItemGroup")
            VALUES
            ('I001','Laptop',1500.00,50,'Electronics'),
            ('I002','Mouse',200.00,200,'Accessories'),
            ('I003','Keyboard',500.00,150,'Accessories'),
            ('I004','Monitor',1500.00,75,'Electronics'),
            ('I005','Headphones',600.00,100,'Accessories')
        """))

        db.execute(text("""
            INSERT INTO "ORDR"
            ("DocNum","DocDate","DocDueDate","CardCode",
             "CardName","DocTotal","DocStatus","Comments")
            VALUES
            (1001,'2026-01-05','2026-01-15','C001',
             'Rahul Sharma',2500.00,'O','First order'),
            (1002,'2026-01-10','2026-01-20','C002',
             'Priya Singh',4500.00,'O','Bulk order'),
            (1003,'2026-01-15','2026-01-25','C003',
             'Amit Kumar',1200.00,'C','Closed order'),
            (1004,'2026-02-01','2026-02-10','C004',
             'Sneha Patel',3200.00,'O','Regular order'),
            (1005,'2026-02-05','2026-02-15','C005',
             'Vikram Nair',5000.00,'O','Large order'),
            (1006,'2026-02-10','2026-02-20','C006',
             'Deepa Reddy',1800.00,'C','Completed'),
            (1007,'2026-03-01','2026-03-10','C007',
             'Suresh Kumar',2200.00,'O','New order'),
            (1008,'2026-03-05','2026-03-15','C008',
             'Anita Desai',3800.00,'O','Priority order'),
            (1009,'2026-03-10','2026-03-20','C009',
             'Rajesh Verma',1500.00,'C','Closed'),
            (1010,'2026-03-15','2026-03-25','C010',
             'Meena Iyer',4200.00,'O','Express order')
        """))
        db.commit()

        result = db.execute(text(
            'SELECT "DocEntry" FROM "ORDR" ORDER BY "DocEntry"'
        ))
        entries = [row[0] for row in result.fetchall()]

        db.execute(text(f"""
            INSERT INTO "RDR1"
            ("DocEntry","ItemCode","ItemName",
             "Quantity","Price","LineTotal")
            VALUES
            ({entries[0]},'I001','Laptop',1,1500.00,1500.00),
            ({entries[0]},'I002','Mouse',5,200.00,1000.00),
            ({entries[1]},'I003','Keyboard',3,500.00,1500.00),
            ({entries[1]},'I004','Monitor',2,1500.00,3000.00),
            ({entries[2]},'I005','Headphones',2,600.00,1200.00),
            ({entries[3]},'I001','Laptop',2,1500.00,3000.00),
            ({entries[3]},'I002','Mouse',1,200.00,200.00),
            ({entries[4]},'I003','Keyboard',5,500.00,2500.00),
            ({entries[4]},'I004','Monitor',1,1500.00,1500.00),
            ({entries[5]},'I005','Headphones',3,600.00,1800.00),
            ({entries[6]},'I001','Laptop',1,1500.00,1500.00),
            ({entries[6]},'I002','Mouse',2,200.00,400.00),
            ({entries[6]},'I003','Keyboard',1,500.00,500.00),
            ({entries[7]},'I004','Monitor',2,1500.00,3000.00),
            ({entries[7]},'I005','Headphones',1,600.00,600.00),
            ({entries[8]},'I001','Laptop',1,1500.00,1500.00),
            ({entries[9]},'I002','Mouse',3,200.00,600.00),
            ({entries[9]},'I003','Keyboard',2,500.00,1000.00),
            ({entries[9]},'I004','Monitor',1,1500.00,1500.00),
            ({entries[9]},'I005','Headphones',2,600.00,1200.00)
        """))
        db.commit()
        print("✅ SAP sample data added!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


def add_sample_customers():
    from app.model.sales_order_model import Customer
    db = next(get_db())
    try:
        existing = db.query(Customer).first()
        if not existing:
            customers = [
                Customer(card_code="C001",
                         card_name="Rahul Sharma",
                         phone="9876543210",
                         email="rahul@email.com",
                         address="Bangalore, Karnataka"),
                Customer(card_code="C002",
                         card_name="Priya Singh",
                         phone="9845678901",
                         email="priya@email.com",
                         address="Mumbai, Maharashtra"),
                Customer(card_code="C003",
                         card_name="Amit Kumar",
                         phone="9756432109",
                         email="amit@email.com",
                         address="Delhi, NCR"),
                Customer(card_code="C004",
                         card_name="Sneha Patel",
                         phone="9654321098",
                         email="sneha@email.com",
                         address="Ahmedabad, Gujarat"),
                Customer(card_code="C005",
                         card_name="Vikram Nair",
                         phone="9543210987",
                         email="vikram@email.com",
                         address="Chennai, Tamil Nadu"),
                Customer(card_code="C006",
                         card_name="Deepa Reddy",
                         phone="9432109876",
                         email="deepa@email.com",
                         address="Hyderabad, Telangana"),
                Customer(card_code="C007",
                         card_name="Suresh Kumar",
                         phone="9321098765",
                         email="suresh@email.com",
                         address="Pune, Maharashtra"),
                Customer(card_code="C008",
                         card_name="Anita Desai",
                         phone="9210987654",
                         email="anita@email.com",
                         address="Surat, Gujarat"),
                Customer(card_code="C009",
                         card_name="Rajesh Verma",
                         phone="9109876543",
                         email="rajesh@email.com",
                         address="Jaipur, Rajasthan"),
                Customer(card_code="C010",
                         card_name="Meena Iyer",
                         phone="9098765432",
                         email="meena@email.com",
                         address="Kochi, Kerala"),
            ]
            db.add_all(customers)
            db.commit()
            print("✅ Sample customers added!")
        else:
            print("✅ Customers already exist!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


# Run on startup
setup_sap_tables()
add_sample_customers()

# Create FastAPI app
app = FastAPI(
    title="SAP B1 Sales API",
    description="Sales Team API - Techative Pvt Ltd Solutions",
    version="1.0.0"
)

# Include routers
app.include_router(order_router)
app.include_router(invoice_router)
app.include_router(return_router)


@app.get("/")
def home():
    return {
        "message": "SAP B1 Sales API is running!",
        "company": "Techative Pvt Ltd Solutions",
        "version": "1.0.0"
    }


@app.get("/customers")
def get_all_customers(db: Session = Depends(get_db)):
    from app.crud.sales_order_crud import get_all_customers
    customers = get_all_customers(db=db)
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
def get_customer(card_code: str,
                  db: Session = Depends(get_db)):
    from app.crud.sales_order_crud import get_customer
    customer = get_customer(db=db, card_code=card_code)
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


@app.get("/query")
def execute_query(sql: str,
                   db: Session = Depends(get_db)):
    try:
        result = db.execute(text(sql))
        rows = result.fetchall()
        columns = result.keys()
        return {
            "data": [
                dict(zip(columns, row))
                for row in rows
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400,
                             detail=str(e))