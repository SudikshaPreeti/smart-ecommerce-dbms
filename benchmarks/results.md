# Benchmark Results

**Environment:** MySQL 8.0 on macOS (Apple Silicon), Python 3.13, 40,315 products, 3,006 orders.

## Query Performance: With vs Without Indexes

| Query | With Index | Without Index | Speedup |
|-------|-----------:|--------------:|--------:|
| `product_by_price_exact` (unit_price = 5.45) | **1.10 ms** · `ref` · 204 rows | **10.21 ms** · `ALL` · 39,785 rows | **9.3×** |
| `product_by_price_range_narrow` (BETWEEN 5 AND 6) | **10.26 ms** · `range` · 4,815 rows | **12.77 ms** · `ALL` · 39,785 rows | 1.2× |
| `orders_by_date_exact` (order_date = '2026-01-01') | **0.15 ms** · `ref` · 1 row | **0.55 ms** · `ALL` · 3,006 rows | **3.6×** |
| `product_by_category` (category_id = 2464) | 0.23 ms · `ref` · 1 row | 0.25 ms (FK index) | — |
| `product_by_name` (LIKE 'CHRISTMAS%') | 1.19 ms · `range` · 429 rows | 1.02 ms | — |
| `orders_by_customer` (customer_id = 12347) | 0.19 ms · `ref` · 12 rows | 0.21 ms (FK index) | — |
| `fulltext_search` (MATCH CHRISTMAS) | 3.54 ms · `fulltext` · 1 row | 3.53 ms | — |
| `interactions_by_user_type` (composite index) | 0.12 ms · `ref` · 1 row | 0.16 ms | — |

## Key Findings

1. **Indexes reduce row scans by 100× or more.** The `product_by_price_exact` query goes from scanning **39,785 rows** to just **204** — a 195× reduction.

2. **The query optimizer is selective.** When the WHERE clause matches > 40% of rows (e.g. `BETWEEN 5 AND 10`), MySQL correctly prefers a full table scan over an index. **Indexes are for selective queries**, not bulk reads.

3. **Composite indexes serve multiple query shapes.** `idx_int_cust_type(customer_id, interaction_type)` is chosen even for queries filtering by `customer_id` alone — MySQL uses the leftmost prefix.

4. **FULLTEXT indexes** (`idx_ft_product`) power `MATCH ... AGAINST` queries with a different algorithm than B-Trees.

5. **Foreign-key-backed indexes cannot be dropped** without removing the FK constraint — this is why `product_by_category` and `orders_by_customer` keep `ref` access in both runs.

## Raw Data

- `results_with_indexes.csv` — benchmark with all indexes present
- `results_without_indexes.csv` — benchmark with `idx_product_price` and `idx_orders_date` dropped

Regenerate with:
```bash
python -m benchmarks.bench