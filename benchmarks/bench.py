"""
Benchmark: Show how MySQL uses indexes via EXPLAIN + timing.

Produces benchmarks/results.csv with:
  - query name
  - avg execution time (ms)
  - access type (ALL, ref, range, fulltext, ...)
  - index used
  - rows scanned
  - EXPLAIN notes
"""
import time
import pandas as pd
from sqlalchemy import text
from backend.db import engine


# -------------------------------------------------------------
# Highly-selective queries → MySQL chooses indexes
# -------------------------------------------------------------
QUERIES = {
    "product_by_category":
        "SELECT * FROM Product WHERE category_id = 2464",

    "product_by_price_exact":
        "SELECT * FROM Product WHERE unit_price = 5.45",

    "product_by_price_range_narrow":
        "SELECT * FROM Product WHERE unit_price BETWEEN 5 AND 6",

    "product_by_name":
        "SELECT * FROM Product WHERE product_name LIKE 'CHRISTMAS%'",

    "orders_by_customer":
        "SELECT * FROM Orders WHERE customer_id = 12347",

    "orders_by_date_exact":
        "SELECT * FROM Orders WHERE order_date = '2026-01-01'",

    "reviews_by_product":
        "SELECT * FROM Reviews WHERE product_id = 7331",

    "interactions_by_user":
        "SELECT * FROM Product_Interactions WHERE customer_id = 12347",

    "interactions_by_user_type":
        "SELECT * FROM Product_Interactions "
        "WHERE customer_id = 12347 AND interaction_type = 'purchase'",

    "fulltext_search":
        "SELECT * FROM Product WHERE MATCH(product_name) AGAINST('CHRISTMAS')",
}


def time_query(q: str, runs: int = 30) -> float:
    """Run query N times and return average milliseconds."""
    with engine.connect() as c:
        c.execute(text(q)).fetchall()  # warm-up
        times = []
        for _ in range(runs):
            t0 = time.perf_counter()
            c.execute(text(q)).fetchall()
            times.append((time.perf_counter() - t0) * 1000)
    return round(sum(times) / len(times), 3)


def explain_query(q: str) -> dict:
    """Return key fields from EXPLAIN for the given query."""
    with engine.connect() as c:
        rows = c.execute(text("EXPLAIN " + q)).mappings().all()
        first = rows[0]
        return {
            "type": first.get("type"),
            "key":  first.get("key") or "(none)",
            "rows": first.get("rows"),
            "note": (first.get("Extra") or "")[:40],
        }


def run():
    print("=" * 100)
    print("Query performance & index usage")
    print("=" * 100)

    results = []
    for name, q in QUERIES.items():
        ms = time_query(q)
        ex = explain_query(q)
        results.append({
            "query":        name,
            "avg_ms":       ms,
            "access_type":  ex["type"],
            "index_used":   ex["key"],
            "rows_scanned": ex["rows"],
            "note":         ex["note"],
        })
        print(f"{name:32} {ms:>7.3f} ms   "
              f"type={str(ex['type']):<10} "
              f"key={str(ex['key']):<24} "
              f"rows={ex['rows']}")

    df = pd.DataFrame(results)
    print("\n=== Summary table ===")
    print(df.to_string(index=False))

    df.to_csv("benchmarks/results.csv", index=False)
    print("\n✅ Saved benchmarks/results.csv")


if __name__ == "__main__":
    run()