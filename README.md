# SAP B1 Multi-Agent Sales System

A conversational AI-powered sales assistant built for **Techative Pvt Ltd Solutions**, integrated with SAP Business One (SAP B1). Users can interact with their SAP B1 sales data in plain English — the system automatically understands the intent, fetches the right data, and responds with professional business reports.

---

## Live Demo

**Deployed URL:** [https://sap-sales-agent-1.onrender.com](https://sap-sales-agent-1.onrender.com)

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Claude Opus 4.7 (Anthropic) |
| Agent Framework | LangGraph + LangChain |
| Backend API | FastAPI |
| Database | PostgreSQL (Render) |
| RAG | ChromaDB + SentenceTransformer |
| Frontend UI | Streamlit |
| Deployment | Render |

---

## Project Structure

```
sap_sales_agent/
├── app/
│   ├── agents/
│   │   ├── salesorder/
│   │   │   ├── sales_order_agent.py     # Sales order router
│   │   │   ├── create_agent.py          # Create new orders
│   │   │   ├── update_agent.py          # Update existing orders
│   │   │   ├── cancel_close_agent.py    # Cancel or close orders
│   │   │   ├── fetch_agent.py           # Fetch and analytics (RAG + Text-to-SQL)
│   │   │   └── validation_agent.py      # Validate customer and stock
│   │   ├── salesinvoice/
│   │   │   └── sales_invoice_agent.py   # Sales invoice operations
│   │   ├── salesreturn/
│   │   │   └── sales_return_agent.py    # Sales return operations
│   │   └── supervisor_agent.py          # Routes messages to correct agent
│   ├── api/
│   │   ├── sales_order_api.py
│   │   ├── sales_invoice_api.py
│   │   ├── sales_return_api.py
│   │   └── generate_sql_api.py
│   ├── crud/
│   │   └── sales_order_crud.py
│   ├── db/
│   │   └── base.py
│   ├── model/
│   │   └── sales_order_model.py
│   ├── schema/
│   │   └── sales_order_schema.py
│   ├── operations/
│   │   ├── utils.py                     # execute_query - direct PostgreSQL
│   │   ├── schema_rag.py                # ChromaDB RAG for schema retrieval
│   │   ├── sap_client.py                # SAP B1 Service Layer API calls
│   │   └── llm_config.py                # Central LLM config (Claude Opus 4.7)
│   └── main.py
├── streamlit_app.py                     # Streamlit chat UI
├── main.py
├── render.yaml
├── requirements.txt
└── .env
```

---

## System Architecture

```
User (Plain English Question)
         |
         v
   Streamlit UI
         |
         v
   Supervisor Agent  <-- Claude Opus 4.7 classifies intent
         |
   ______|______________________________________
   |          |              |                 |
   v          v              v                 v
Sales       Fetch         Sales             Sales
Order       Agent         Invoice           Return
Agent       (RAG +        Agent             Agent
            Text-to-SQL)
   |          |              |                 |
   v          v              v                 v
SAP B1    PostgreSQL      SAP B1            SAP B1
Service   (Direct)        Service           Service
Layer     + ChromaDB      Layer             Layer
```

---

## Agent Overview

### Supervisor Agent
Routes every user message to the correct sub-agent based on intent classification using Claude Opus 4.7.

Categories:
- `order` — Sales order operations
- `invoice` — Sales invoice operations
- `return` — Sales return operations
- `fetch` — Data retrieval and analytics

---

### Sales Order Agent
Handles all sales order operations with 5 sub-agents:

| Sub-Agent | Purpose |
|---|---|
| Create Agent | Validates customer and stock, creates new order via SAP B1 |
| Update Agent | Fetches order details and updates comments |
| Cancel/Close Agent | Cancels or closes an existing order |
| Fetch Agent | Retrieves order data using RAG + Text-to-SQL |
| Validation Agent | Validates customer credit and item stock |

---

### Fetch Agent (RAG + Text-to-SQL)
The most important agent for data retrieval. Works in 3 steps:

```
Step 1 — User asks a question in plain English
Step 2 — RAG retrieves relevant SAP B1 schema from ChromaDB
Step 3 — Claude Opus 4.7 generates correct SQL using schema context
Step 4 — SQL runs directly on PostgreSQL
Step 5 — Claude formats result as a professional business report
```

Available tools:
- `get_all_customers` — List all customers
- `get_customer_info` — Details of one customer
- `get_all_items` — List all items/products
- `get_item_info` — Stock and price of one item
- `get_all_orders` — All sales orders
- `get_orders_by_customer` — Orders for one customer
- `get_open_orders` — Open/pending orders only
- `get_order_summary` — Statistics and totals
- `text_to_sql_with_rag` — Complex analytical queries via RAG

---

### Sales Invoice Agent
Handles invoice operations via SAP B1 Service Layer:
- Create invoice
- Cancel invoice
- Close invoice
- Reopen invoice

---

### Sales Return Agent
Handles return operations via SAP B1 Service Layer:
- Create return
- Cancel return
- Close return
- Reopen return

---

## Database Tables

### SAP B1 Tables (PostgreSQL on Render)

| Table | Description |
|---|---|
| OCRD | Customer Master — 10 customers (C001 to C010) |
| OITM | Item Master — 5 items (I001 to I005) |
| ORDR | Sales Order Header |
| RDR1 | Sales Order Lines |
| OINV | Sales Invoice Header |
| INV1 | Sales Invoice Lines |
| ORDN | Sales Return Header |
| RDN1 | Sales Return Lines |

### Sample Data

**Customers:** C001 to C010

**Items:**

| Code | Item |
|---|---|
| I001 | Laptop |
| I002 | Mouse |
| I003 | Keyboard |
| I004 | Monitor |
| I005 | Headphones |

**Orders:** DocNum 1001 to 1010

---

## SAP B1 Service Layer Endpoints

### Sales Orders
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/b1s/v2/Orders` | Create order |
| PATCH | `/b1s/v2/Orders({DocEntry})` | Update order |
| POST | `/b1s/v2/Orders({DocEntry})/Cancel` | Cancel order |
| POST | `/b1s/v2/Orders({DocEntry})/Close` | Close order |

### Sales Invoices
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/b1s/v2/Invoices` | Create invoice |
| POST | `/b1s/v2/Invoices({DocEntry})/Cancel` | Cancel invoice |
| POST | `/b1s/v2/Invoices({DocEntry})/Close` | Close invoice |
| POST | `/b1s/v2/Invoices({DocEntry})/Reopen` | Reopen invoice |

### Sales Returns
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/b1s/v2/Returns` | Create return |
| POST | `/b1s/v2/Returns({DocEntry})/Cancel` | Cancel return |
| POST | `/b1s/v2/Returns({DocEntry})/Close` | Close return |
| POST | `/b1s/v2/Returns({DocEntry})/Reopen` | Reopen return |

---

## Setup and Installation

### Prerequisites
- Python 3.10+
- PostgreSQL
- Anthropic API Key (Claude Opus 4.7)
- Groq API Key (optional fallback)

### Installation

```bash
# Clone the repository
git clone https://github.com/Dhanush-K-Git/sap-sales-agent.git
cd sap-sales-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://user:password@host/dbname
SAP_BASE_URL=https://localhost:50000/b1s/v2
```

### Run Locally

```bash
# Start Streamlit UI
streamlit run streamlit_app.py

# Start FastAPI backend
uvicorn app.main:app --reload
```

---

## Sample Queries

| Query | Agent Used |
|---|---|
| "Give me the list of customers" | Fetch Agent |
| "Show me all sales orders" | Fetch Agent |
| "Show open orders" | Fetch Agent |
| "Give me sales summary" | Fetch Agent |
| "Which customer has highest order value?" | Fetch Agent (RAG) |
| "Create order for C001 with 2 Laptops" | Create Agent |
| "Update order 1001 comments" | Update Agent |
| "Cancel order 1002" | Cancel Agent |
| "Validate customer C003" | Validation Agent |
| "Create invoice for C001" | Invoice Agent |
| "Create return for C002" | Return Agent |

---

## Response Format

All responses follow a professional business report format:

```
Hello! Here is your Sales Order Report.

---
SUMMARY
--------------------------
Total Orders   : 10
Open Orders    : 6
Closed Orders  : 4
Total Value    : Rs.12,50,000
Average Order  : Rs.1,25,000
--------------------------

ORDER DETAILS

| Order No | Date       | Customer      | Item    | Qty | Total       | Status   |
|----------|------------|--------------|---------|-----|-------------|----------|
| 1001     | 2026-04-01 | Rahul Traders | Laptop  | 2   | Rs.1,00,000 | [Open]   |
| 1002     | 2026-04-02 | Singh Exports | Mouse   | 10  | Rs.15,000   | [Closed] |

---
KEY INSIGHTS
- Highest order   : Order 1001 - Rs.1,00,000
- Most active     : C001 Rahul Traders - 3 orders
- Most ordered    : Laptop - 8 units total
- Attention       : 6 open orders pending follow-up
```

---

## Development Team

| Name | Role |
|---|---|
| Dhanush K | AI Engineering Intern — Sales Agent |

**Company:** Techative Pvt Ltd Solutions

---

## License

This project is proprietary and developed for internal use at Techative Pvt Ltd Solutions.
