# Save as test_rag.py in project root
from app.operations.schema_rag import get_schema_from_rag

print("\n" + "="*45)
print(" RAG TEST")
print("="*45)

# Test 1
q1 = "give me list of customers"
print(f"\nQuery: '{q1}'")
print(f"Schema found:\n{get_schema_from_rag(q1)}")

# Test 2
q2 = "which customer has highest order value"
print(f"\nQuery: '{q2}'")
print(f"Schema found:\n{get_schema_from_rag(q2)}")

# Test 3
q3 = "show me open orders"
print(f"\nQuery: '{q3}'")
print(f"Schema found:\n{get_schema_from_rag(q3)}")

print("\n" + "="*45)