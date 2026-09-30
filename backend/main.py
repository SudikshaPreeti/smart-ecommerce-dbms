"""
FastAPI application for Smart E-Commerce.
"""
import os
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv

from recommendation.hybrid import get_hybrid_recommendations

load_dotenv()

DB_URL = (
    f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{quote_plus(os.getenv('DB_PASS',''))}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
engine = create_engine(DB_URL, pool_pre_ping=True, pool_size=10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Smart E-Commerce API starting...")
    yield
    print("👋 Shutting down...")


app = FastAPI(title="Smart E-Commerce API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class OrderItem(BaseModel):
    product_id: int
    qty: int


class OrderPayload(BaseModel):
    customer_id: int
    items: list[OrderItem]


@app.get("/")
def root():
    return {"status": "ok", "service": "smart-ecommerce"}


@app.get("/products")
def list_products(limit: int = 20):
    with engine.connect() as c:
        rows = c.execute(text(
            "SELECT product_id, product_name, unit_price, stock_quantity "
            "FROM Product LIMIT :l"
        ), {"l": limit}).mappings().all()
    return rows


@app.get("/products/{pid}")
def get_product(pid: int):
    with engine.connect() as c:
        row = c.execute(text(
            "SELECT * FROM Product WHERE product_id = :p"
        ), {"p": pid}).mappings().first()
    if not row:
        raise HTTPException(404, "Product not found")
    return row


@app.get("/categories")
def list_categories():
    with engine.connect() as c:
        rows = c.execute(text(
            "SELECT * FROM vw_category_summary ORDER BY total_revenue DESC"
        )).mappings().all()
    return rows


@app.get("/top-rated")
def top_rated(limit: int = 10):
    with engine.connect() as c:
        rows = c.execute(text(
            "SELECT * FROM vw_top_rated LIMIT :l"
        ), {"l": limit}).mappings().all()
    return rows


@app.post("/orders")
def place_order(payload: OrderPayload):
    items_json = json.dumps([item.dict() for item in payload.items])
    with engine.begin() as c:
        c.execute(text("CALL sp_place_order(:cid, :items, @oid)"), {
            "cid": payload.customer_id,
            "items": items_json,
        })
        oid = c.execute(text("SELECT @oid")).scalar()
    return {"order_id": oid}

@app.get("/orders/recent")
def recent_orders(limit: int = 10):
    with engine.connect() as c:
        rows = c.execute(text("""
            SELECT o.order_id, cu.full_name, o.status,
                   o.total_amount, o.order_date
            FROM Orders o
            JOIN Customer cu ON cu.customer_id = o.customer_id
            ORDER BY o.order_id DESC
            LIMIT :l
        """), {"l": limit}).mappings().all()
    return rows


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    with engine.connect() as c:
        order = c.execute(text("""
            SELECT o.order_id, cu.full_name, o.status,
                   o.total_amount, o.order_date
            FROM Orders o
            JOIN Customer cu ON cu.customer_id = o.customer_id
            WHERE o.order_id = :o
        """), {"o": order_id}).mappings().first()

        if not order:
            raise HTTPException(404, "Order not found")

        items = c.execute(text("""
            SELECT oi.product_id, p.product_name,
                   oi.quantity, oi.unit_price,
                   (oi.quantity * oi.unit_price) AS subtotal
            FROM Order_Items oi
            JOIN Product p ON p.product_id = oi.product_id
            WHERE oi.order_id = :o
        """), {"o": order_id}).mappings().all()

    return {"order": order, "items": items}


@app.get("/customers/{cid}/summary")
def customer_summary(cid: int):
    with engine.connect() as c:
        rows = c.execute(text("CALL sp_customer_summary(:cid)"), {"cid": cid}).mappings().all()
    if not rows:
        raise HTTPException(404, "Customer not found")
    return rows[0]


@app.get("/recommendations/{user_id}")
def recommendations(user_id: int, top_n: int = 10):
    try:
        ids = get_hybrid_recommendations(user_id, top_n=top_n)
    except Exception as e:
        raise HTTPException(500, f"Recommender error: {e}")

    if not ids:
        return []

    placeholders = ",".join(str(i) for i in ids)
    with engine.connect() as c:
        rows = c.execute(text(
            f"SELECT product_id, product_name, unit_price "
            f"FROM Product WHERE product_id IN ({placeholders})"
        )).mappings().all()
    return rows