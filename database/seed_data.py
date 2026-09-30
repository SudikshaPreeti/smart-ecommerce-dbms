"""
Seed MySQL database from preprocessed CSVs.
Loads: Customer, Category, Product, Product_Interactions
"""
import os
import pandas as pd
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_URL = (
    f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{quote_plus(os.getenv('DB_PASS', ''))}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
print("Connecting to DB:", DB_URL.split("@")[-1])
engine = create_engine(DB_URL)


def check_env():
    required = ["DB_USER", "DB_PASS", "DB_HOST", "DB_NAME"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise SystemExit(f"❌ Missing in .env: {missing}")


def load_customers(df):
    customers = df[["CustomerID", "Country"]].drop_duplicates("CustomerID").copy()
    customers.columns = ["customer_id", "country"]
    customers["full_name"] = "Customer " + customers["customer_id"].astype(str)
    customers["email"] = customers["customer_id"].astype(str) + "@example.com"
    customers["phone"] = None
    customers["signup_date"] = pd.Timestamp("2023-01-01").date()
    customers = customers[
        ["customer_id", "full_name", "email", "phone", "country", "signup_date"]
    ]

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM Customer"))
        customers.to_sql("Customer", conn, if_exists="append", index=False)
    print(f"✅ Loaded {len(customers)} customers")


def load_categories(df):
    # Normalize BEFORE deduplication (MySQL collation is case-insensitive)
    cats = df[["Category"]].copy()
    cats["category_name"] = (
        cats["Category"].astype(str).str.strip().str.upper().str.slice(0, 80)
    )
    cats = cats[
        (cats["category_name"] != "")
        & (cats["category_name"] != "NAN")
        & (cats["category_name"] != "NONE")
    ]
    cats = cats.drop_duplicates("category_name").reset_index(drop=True)
    cats["description"] = "Auto-generated category"
    cats = cats[["category_name", "description"]]

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM Category"))
        cats.to_sql("Category", conn, if_exists="append", index=False)
    print(f"✅ Loaded {len(cats)} categories")


def load_products(df):
    cat_map = (
        pd.read_sql("SELECT category_id, category_name FROM Category", engine)
        .set_index("category_name")["category_id"]
        .to_dict()
    )

    prods = df.drop_duplicates("StockCode")[
        ["StockCode", "Description", "Category", "UnitPrice"]
    ].copy()
    prods.columns = ["stock_code", "product_name", "category_name", "unit_price"]
    prods["category_name"] = prods["category_name"].astype(str).str.upper()
    prods["category_id"] = prods["category_name"].map(cat_map)
    prods["stock_quantity"] = 500
    prods = prods.dropna(subset=["category_id", "product_name", "stock_code"])
    prods = prods[prods["unit_price"] >= 0]
    prods = prods[
        ["stock_code", "product_name", "category_id", "unit_price", "stock_quantity"]
    ]

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM Product"))
        prods.to_sql("Product", conn, if_exists="append", index=False, chunksize=500)
    print(f"✅ Loaded {len(prods)} products")


def load_interactions():
    inter = pd.read_csv("data/processed/interactions.csv")
    prod_map = (
        pd.read_sql("SELECT product_id, stock_code FROM Product", engine)
        .set_index("stock_code")["product_id"]
        .to_dict()
    )

    inter["product_id"] = inter["StockCode"].map(prod_map)
    inter = inter.dropna(subset=["product_id"])
    inter["product_id"] = inter["product_id"].astype(int)
    inter["customer_id"] = inter["CustomerID"].astype(int)
    inter["interaction_type"] = inter["interaction_type"].astype(str)
    inter["interaction_time"] = pd.to_datetime(inter["interaction_time"])

    inter = inter[["customer_id", "product_id", "interaction_type", "interaction_time"]]

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM Product_Interactions"))
        inter.to_sql(
            "Product_Interactions", conn, if_exists="append", index=False, chunksize=5000
        )
    print(f"✅ Loaded {len(inter)} interactions")


def main():
    print("=" * 50)
    print("🚀 Starting seed process")
    print("=" * 50)
    check_env()

    print("📖 Reading cleaned transactions...")
    df = pd.read_csv("data/processed/transactions_clean.csv")
    print(f"  Rows: {len(df)}")

    load_customers(df)
    load_categories(df)
    load_products(df)
    load_interactions()

    print("\n🎉 Seed complete!")


if __name__ == "__main__":
    main()