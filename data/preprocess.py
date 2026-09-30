import pandas as pd

CATEGORY_RULES = [
    ("CHRISTMAS",  ["christmas", "xmas", "santa", "reindeer", "advent", "noel"]),
    ("BAGS",       ["bag", "tote", "handbag", "purse", "backpack"]),
    ("LIGHTS",     ["light", "lamp", "candle", "lantern", "torch"]),
    ("KITCHEN",    ["mug", "cup", "plate", "bowl", "jug", "teapot", "spoon",
                    "fork", "knife", "kitchen", "bottle"]),
    ("DECOR",      ["frame", "clock", "mirror", "sign", "ornament",
                    "decoration", "holder", "hanger"]),
    ("TOYS",       ["toy", "game", "doll", "puzzle", "playhouse", "children"]),
    ("GARDEN",     ["garden", "plant", "flower", "watering", "bird"]),
    ("STATIONERY", ["card", "notebook", "pen", "pencil", "journal", "paper"]),
    ("JEWELLERY",  ["necklace", "bracelet", "earring", "ring", "jewel", "bead"]),
    ("TEXTILES",   ["towel", "cushion", "blanket", "apron", "cloth", "fabric"]),
    ("STORAGE",    ["box", "tin", "container", "basket", "jar"]),
    ("PARTY",      ["party", "balloon", "banner", "birthday"]),
    ("BABY",       ["baby", "nursery", "pram"]),
    ("SEASONAL",   ["easter", "halloween", "valentine", "summer", "winter"]),
]

def categorize(description):
    if pd.isna(description):
        return "OTHER"
    desc = str(description).lower()
    for cat, keywords in CATEGORY_RULES:
        if any(kw in desc for kw in keywords):
            return cat
    return "OTHER"

def clean():
    df = pd.read_excel("data/raw/online_retail.xlsx")
    print("Raw shape:", df.shape)

    df.columns = [c.strip().replace(" ", "_") for c in df.columns]
    df = df.dropna(subset=["CustomerID"])
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df["CustomerID"] = df["CustomerID"].astype(int)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

    df["Category"] = df["Description"].apply(categorize)

    df.to_csv("data/processed/transactions_clean.csv", index=False)
    print("✅ Cleaned shape:", df.shape)
    print("\nCategory distribution:")
    print(df["Category"].value_counts())

if __name__ == "__main__":
    clean()