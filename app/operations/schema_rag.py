# app/operations/schema_rag.py
# Loads ChromaDB and SentenceTransformer ONCE
# Reuses on every query — saves 1-2 seconds

import chromadb
from sentence_transformers import SentenceTransformer

# ─────────────────────────────────────────
# SINGLETON PATTERN — load once at startup
# ─────────────────────────────────────────
_embedding_model = None
_collection      = None


def _get_rag():
    """Returns (embedding_model, collection) — loaded once."""
    global _embedding_model, _collection

    if _embedding_model is None:
        print("Loading RAG embedding model...")
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("RAG model loaded")

    if _collection is None:
        client      = chromadb.Client()
        _collection = client.get_or_create_collection(name="sap_schema")

        if _collection.count() == 0:
            _load_schema(_collection, _embedding_model)

    return _embedding_model, _collection


def _load_schema(collection, model):
    """Load SAP B1 schema into ChromaDB — only once."""
    schema_data = [
        {"id": "1",  "text": "Table: ORDR Column: DocEntry primary key sales order id"},
        {"id": "2",  "text": "Table: ORDR Column: DocNum sales order number document number"},
        {"id": "3",  "text": "Table: ORDR Column: DocDate sales order date transaction date"},
        {"id": "4",  "text": "Table: ORDR Column: DocDueDate due date delivery date"},
        {"id": "5",  "text": "Table: ORDR Column: CardCode customer code customer id"},
        {"id": "6",  "text": "Table: ORDR Column: CardName customer name buyer name"},
        {"id": "7",  "text": "Table: ORDR Column: DocTotal total amount grand total order value"},
        {"id": "8",  "text": "Table: ORDR Column: DocStatus order status O open C closed"},
        {"id": "9",  "text": "Table: ORDR Column: Comments remarks notes"},
        {"id": "10", "text": "Table: RDR1 Column: DocEntry foreign key join ORDR"},
        {"id": "11", "text": "Table: RDR1 Column: ItemCode product code item id"},
        {"id": "12", "text": "Table: RDR1 Column: ItemName product name description"},
        {"id": "13", "text": "Table: RDR1 Column: Quantity sales quantity ordered"},
        {"id": "14", "text": "Table: RDR1 Column: Price unit price item price"},
        {"id": "15", "text": "Table: RDR1 Column: LineTotal line total subtotal"},
        {"id": "16", "text": "Table: OCRD Column: CardCode customer code primary key"},
        {"id": "17", "text": "Table: OCRD Column: CardName customer name full name"},
        {"id": "18", "text": "Table: OCRD Column: Phone customer phone number"},
        {"id": "19", "text": "Table: OCRD Column: Email customer email address"},
        {"id": "20", "text": "Table: OCRD Column: CreditLimit credit limit maximum"},
        {"id": "21", "text": "Table: OCRD Column: Balance outstanding balance amount due"},
        {"id": "22", "text": "Table: OITM Column: ItemCode product code primary key"},
        {"id": "23", "text": "Table: OITM Column: ItemName product name description"},
        {"id": "24", "text": "Table: OITM Column: Price selling price unit price"},
        {"id": "25", "text": "Table: OITM Column: Stock available stock inventory"},
        {"id": "26", "text": "Table: OITM Column: ItemGroup item category product group"},
    ]

    for item in schema_data:
        emb = model.encode(item["text"]).tolist()
        collection.add(
            ids=[item["id"]],
            embeddings=[emb],
            documents=[item["text"]]
        )
    print("SAP schema loaded into ChromaDB")


def get_schema_from_rag(query: str) -> str:
    """Find relevant schema — fast because model is pre-loaded."""
    model, collection = _get_rag()

    query_emb = model.encode(query).tolist()
    results   = collection.query(
        query_embeddings=[query_emb],
        n_results=7
    )

    docs   = results["documents"][0]
    tables = {}

    for doc in docs:
        parts  = doc.split("Column:")
        table  = parts[0].replace("Table:", "").strip()
        column = parts[1].strip().split()[0]
        if table not in tables:
            tables[table] = []
        if column not in tables[table]:
            tables[table].append(column)

    context = ""
    for table, cols in tables.items():
        context += f"\nTable: {table}\nColumns:\n"
        for col in cols:
            context += f"  - {col}\n"

    return context.strip()