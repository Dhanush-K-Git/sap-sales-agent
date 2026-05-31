import requests

# Test 1 — SELECT *
print("=== TEST 1: SELECT * ===")
r = requests.get(
    "http://vzone.in:1662/api/GetMethod/GetData",
    params={"query": "SELECT TOP 5 * FROM OCRD"}
)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")

print("\n=== TEST 2: Specific columns ===")
r2 = requests.get(
    "http://vzone.in:1662/api/GetMethod/GetData",
    params={"query": 'SELECT TOP 5 "CardCode", "CardName" FROM OCRD'}
)
print(f"Status: {r2.status_code}")
print(f"Response: {r2.text[:500]}")

print("\n=== TEST 3: Orders ===")
r3 = requests.get(
    "http://vzone.in:1662/api/GetMethod/GetData",
    params={"query": "SELECT TOP 5 * FROM ORDR"}
)
print(f"Status: {r3.status_code}")
print(f"Response: {r3.text[:500]}")