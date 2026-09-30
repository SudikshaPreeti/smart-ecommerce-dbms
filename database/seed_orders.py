"""
Seed sample orders, payments, and reviews so views have real data.
"""
import os
import random
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_URL = (
    f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{quote_plus(os.getenv('DB_PASS',''))}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
engine = create_engine(DB_URL)


def main():
    random.seed(42)

    with engine.begin() as conn:
        print("Clearing old orders/payments/reviews/wishlist...")
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        for t in ["Order_Items", "Payment", "Reviews", "Wishlist", "Orders"]:
            conn.execute(text(f"DELETE FROM {t}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

        customers = [r[0] for r in conn.execute(text("SELECT customer_id FROM Customer")).fetchall()]
        products = conn.execute(text(
            "SELECT product_id, unit_price FROM Product WHERE unit_price > 0"
        )).fetchall()

        if not customers or not products:
            raise SystemExit("❌ No customers or products. Run seed_data.py first.")

        NUM_ORDERS = 500
        NUM_REVIEWS = 800
        NUM_WISHLIST = 300

        print(f"Creating {NUM_ORDERS} orders...")
        statuses = ["PAID", "SHIPPED", "DELIVERED", "PENDING"]
        for i in range(NUM_ORDERS):
            cust = random.choice(customers)
            status = random.choices(statuses, weights=[0.4, 0.3, 0.25, 0.05])[0]
            order_date = datetime.now() - timedelta(days=random.randint(0, 365))

            # Insert order
            result = conn.execute(text("""
                INSERT INTO Orders (customer_id, order_date, status, total_amount)
                VALUES (:c, :d, :s, 0)
            """), {"c": cust, "d": order_date, "s": status})
            order_id = result.lastrowid

            # Add 1–5 items
            num_items = random.randint(1, 5)
            chosen = random.sample(products, min(num_items, len(products)))
            total = 0
            for pid, price in chosen:
                qty = random.randint(1, 3)
                conn.execute(text("""
                    INSERT INTO Order_Items (order_id, product_id, quantity, unit_price)
                    VALUES (:o, :p, :q, :u)
                """), {"o": order_id, "p": pid, "q": qty, "u": float(price)})
                total += qty * float(price)

            conn.execute(text(
                "UPDATE Orders SET total_amount = :t WHERE order_id = :o"
            ), {"t": total, "o": order_id})

            # Payment for non-cancelled orders
            if status in ("PAID", "SHIPPED", "DELIVERED"):
                conn.execute(text("""
                    INSERT INTO Payment (order_id, method, amount, status)
                    VALUES (:o, :m, :a, 'SUCCESS')
                """), {
                    "o": order_id,
                    "m": random.choice(["CARD", "UPI", "NETBANKING", "COD"]),
                    "a": total,
                })

        print(f"Creating {NUM_REVIEWS} reviews...")
        seen = set()
        for _ in range(NUM_REVIEWS):
            cust = random.choice(customers)
            pid, _ = random.choice(products)
            key = (cust, pid)
            if key in seen:
                continue
            seen.add(key)
            try:
                conn.execute(text("""
                    INSERT INTO Reviews (customer_id, product_id, rating, comment)
                    VALUES (:c, :p, :r, :m)
                """), {
                    "c": cust, "p": pid,
                    "r": random.choices([1,2,3,4,5], weights=[5,10,20,35,30])[0],
                    "m": random.choice([
                        "Great product!", "Loved it", "Value for money",
                        "Not as expected", "Would buy again", "Excellent quality",
                        "Fast delivery", "Could be better", "Perfect gift",
                    ]),
                })
            except Exception:
                pass

        print(f"Creating {NUM_WISHLIST} wishlist entries...")
        seen = set()
        for _ in range(NUM_WISHLIST):
            cust = random.choice(customers)
            pid, _ = random.choice(products)
            key = (cust, pid)
            if key in seen:
                continue
            seen.add(key)
            try:
                conn.execute(text("""
                    INSERT INTO Wishlist (customer_id, product_id)
                    VALUES (:c, :p)
                """), {"c": cust, "p": pid})
            except Exception:
                pass

    print("\n🎉 Orders, payments, reviews, wishlist seeded!")


if __name__ == "__main__":
    main()