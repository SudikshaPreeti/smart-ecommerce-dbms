"""
Extract data from MySQL for the recommendation engine.
"""
import os
import pandas as pd
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{quote_plus(os.getenv('DB_PASS',''))}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)


def load_interactions():
    q = """
        SELECT customer_id, product_id, interaction_type, interaction_time
        FROM Product_Interactions
    """
    return pd.read_sql(q, engine)


def load_products():
    q = """
        SELECT product_id, product_name, category_id, unit_price
        FROM Product
    """
    return pd.read_sql(q, engine)


def load_ratings():
    q = """
        SELECT customer_id, product_id, rating
        FROM Reviews
    """
    return pd.read_sql(q, engine)


def load_orders():
    q = """
        SELECT o.customer_id, oi.product_id, oi.quantity, oi.unit_price, o.order_date
        FROM Orders o
        JOIN Order_Items oi ON oi.order_id = o.order_id
    """
    return pd.read_sql(q, engine)


if __name__ == "__main__":
    print("Interactions:", load_interactions().shape)
    print("Products:    ", load_products().shape)
    print("Ratings:     ", load_ratings().shape)
    print("Orders:      ", load_orders().shape)