import pandas as pd, random

df = pd.read_csv("data/processed/transactions_clean.csv")
customers = df["CustomerID"].unique()
products  = df["StockCode"].unique()

rows = []
for _ in range(20000):
    rows.append({
        "CustomerID": random.choice(customers),
        "StockCode":  random.choice(products),
        "interaction_type": random.choices(
            ["view", "wishlist", "addtocart", "purchase"],
            weights=[0.6, 0.1, 0.2, 0.1]
        )[0],
        "interaction_time": pd.Timestamp("2024-01-01") +
                            pd.Timedelta(minutes=random.randint(0, 500000))
    })

pd.DataFrame(rows).to_csv("data/processed/interactions.csv", index=False)
print("✅ Interactions generated:", len(rows))