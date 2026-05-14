import chromadb
from sentence_transformers import SentenceTransformer

# ─────────────────────────────────────────────
# 🧠 INITIALIZE MODELS
# ─────────────────────────────────────────────
print("Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client()
collection = client.get_or_create_collection(name="sap_schema")

# ─────────────────────────────────────────────
# 📊 SAP B1 SCHEMA DATA
# ─────────────────────────────────────────────
schema_data = [
    # ORDR - Sales Order Header
    {
        "id": "1",
        "text": "Table: ORDR Column: DocEntry primary key sales order id document id unique identifier"
    },
    {
        "id": "2",
        "text": "Table: ORDR Column: DocNum sales order number document number order id"
    },
    {
        "id": "3",
        "text": "Table: ORDR Column: DocDate sales order date order date transaction date created date"
    },
    {
        "id": "4",
        "text": "Table: ORDR Column: DocDueDate due date delivery date expected date"
    },
    {
        "id": "5",
        "text": "Table: ORDR Column: CardCode customer code customer id vendor code"
    },
    {
        "id": "6",
        "text": "Table: ORDR Column: CardName customer name vendor name party name buyer name"
    },
    {
        "id": "7",
        "text": "Table: ORDR Column: DocTotal total amount grand total order value sales total"
    },
    {
        "id": "8",
        "text": "Table: ORDR Column: DocStatus order status O means open C means closed cancelled"
    },
    {
        "id": "9",
        "text": "Table: ORDR Column: Comments remarks notes additional info"
    },
    # RDR1 - Sales Order Lines
    {
        "id": "10",
        "text": "Table: RDR1 Column: DocEntry foreign key join ORDR sales order line relation"
    },
    {
        "id": "11",
        "text": "Table: RDR1 Column: ItemCode product code item id sku product id"
    },
    {
        "id": "12",
        "text": "Table: RDR1 Column: ItemName product name item name description product description"
    },
    {
        "id": "13",
        "text": "Table: RDR1 Column: Quantity sales quantity ordered quantity total items"
    },
    {
        "id": "14",
        "text": "Table: RDR1 Column: Price unit price item price cost per unit"
    },
    {
        "id": "15",
        "text": "Table: RDR1 Column: LineTotal line total subtotal amount per item"
    },
    # OCRD - Customer Master
    {
        "id": "16",
        "text": "Table: OCRD Column: CardCode customer code primary key customer id"
    },
    {
        "id": "17",
        "text": "Table: OCRD Column: CardName customer name full name party name"
    },
    {
        "id": "18",
        "text": "Table: OCRD Column: Phone customer phone number mobile contact number"
    },
    {
        "id": "19",
        "text": "Table: OCRD Column: Email customer email address mail"
    },
    {
        "id": "20",
        "text": "Table: OCRD Column: Address customer address location city"
    },
    {
        "id": "21",
        "text": "Table: OCRD Column: CreditLimit credit limit maximum credit allowed"
    },
    {
        "id": "22",
        "text": "Table: OCRD Column: Balance outstanding balance amount due"
    },
    # OITM - Item Master
    {
        "id": "23",
        "text": "Table: OITM Column: ItemCode product code primary key item id sku"
    },
    {
        "id": "24",
        "text": "Table: OITM Column: ItemName product name item name description"
    },
    {
        "id": "25",
        "text": "Table: OITM Column: Price selling price unit price cost"
    },
    {
        "id": "26",
        "text": "Table: OITM Column: Stock available stock inventory quantity in hand"
    },
    {
        "id": "27",
        "text": "Table: OITM Column: ItemGroup item category product group type"
    }
]

# Load schema into ChromaDB
if collection.count() == 0:
    for item in schema_data:
        emb = embedding_model.encode(
            item["text"]
        ).tolist()
        collection.add(
            ids=[item["id"]],
            embeddings=[emb],
            documents=[item["text"]]
        )
    print("✅ Schema loaded into ChromaDB!")


def get_schema_from_rag(query: str) -> str:
    """
    Find relevant schema based on user query
    using RAG (Retrieval Augmented Generation)
    """
    # Convert query to embedding
    query_emb = embedding_model.encode(query).tolist()

    # Find top 7 relevant schema items
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=7
    )

    docs = results["documents"][0]
    tables = {}

    # Parse results into table → columns mapping
    for doc in docs:
        parts = doc.split("Column:")
        table = parts[0].replace(
            "Table:", ""
        ).strip()
        column = parts[1].strip().split()[0]

        if table not in tables:
            tables[table] = []
        if column not in tables[table]:
            tables[table].append(column)

    # Build context string
    context = ""
    for table, cols in tables.items():
        context += f"\nTable: {table}\nColumns:\n"
        for col in cols:
            context += f"  - {col}\n"

    return context.strip()