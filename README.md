# 🛒 Smart E-Commerce Database Management & Personalised Product Recommendation System

A full-stack e-commerce system built with **MySQL**, **Python (FastAPI)**, and **machine learning** for personalised product recommendations.

## 🏗️ Architecture
Browser (HTML/CSS/JS + Chart.js) ──► FastAPI (Python) ──► MySQL 8.0
│
├── recommendation/ (scikit-learn)
└── sqlalchemy ORM


## ✨ Features

### Database Layer (Advanced DBMS)
- **9 normalized tables** (3NF) with PK/FK/CHECK constraints
- **17 indexes** — BTREE, composite, FULLTEXT
- **4 SQL views** — product sales, customer LTV, top-rated, category summary
- **2 stored procedures** — transaction-safe order placement, customer summary
- **3 triggers** — auto stock decrement, cancel-restore stock, auto-log purchases
- **Transactions** — atomic order+items+payment flows

### Recommendation Engine (Machine Learning)
- **Collaborative filtering** — user-item matrix + cosine similarity
- **Content-based filtering** — TF-IDF over product names + categories
- **Hybrid recommender** — weighted blend (α = 0.6 CF + 0.4 content)

### API & Frontend
- **FastAPI** REST endpoints for products, categories, orders, recommendations
- **Interactive dashboard** with real-time KPIs, category revenue chart, top-rated products
- **Place Order** form exercising the full stored procedure + trigger chain

## 🧰 Tech Stack

| Layer | Tech |
|-------|------|
| Database | MySQL 8.0 |
| Backend | Python 3.13, FastAPI, SQLAlchemy |
| ML | Pandas, NumPy, scikit-learn |
| Frontend | HTML5, CSS3, JavaScript, Chart.js |
| Data | UCI Online Retail Dataset (541,909 rows) |

## to run this -
source .venv/bin/activate
mysql -u root -p < database/schema.sql
python database/seed_data.py

terminals:
1. frontend-  python -m http.server 5500 --directory frontend
2. backend - uvicorn backend.main:app --reload

## Configure MySQL:
mysql -u root -p < database/schema.sql
mysql -u root -p < database/indexes.sql
mysql -u root -p < database/views.sql
mysql -u root -p < database/procedures.sql
mysql -u root -p < database/triggers.sql

## create .env
DB_USER=root
DB_PASS=your_password
DB_HOST=localhost
DB_NAME=smart_ecommerce

## 📊 Performance Benchmarks

Measured on 40,315 products and 3,006 orders. Full results in `benchmarks/results.md`.

| Query | With Index | Without Index | Speedup |
|-------|-----------:|--------------:|--------:|
| Product by exact price | **1.10 ms** | 10.21 ms | **9.3×** |
| Product by price range | **10.26 ms** | 12.77 ms | 1.2× |
| Orders by exact date | **0.15 ms** | 0.55 ms | **3.6×** |

**Key insight:** indexes cut row scans by up to 195×. MySQL only uses an index when the query is selective — for range queries matching >40% of rows, it correctly prefers a full scan.
