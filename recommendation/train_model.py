"""
Train & persist recommender artifacts for the API to load.
"""
import pickle
import os
from recommendation.extract import load_interactions, load_products
from recommendation.collaborative import build_user_item_matrix
from recommendation.content_based import build_content_model


def train():
    print("Loading data...")
    interactions = load_interactions()
    products     = load_products()

    print("Building collaborative matrix...")
    matrix = build_user_item_matrix(interactions)

    print("Building content model...")
    prod_df, sim = build_content_model(products)

    artifacts = {
        "matrix":   matrix,
        "products": prod_df,
        "sim":      sim,
    }

    out = "recommendation/artifacts.pkl"
    with open(out, "wb") as f:
        pickle.dump(artifacts, f)

    print(f"✅ Saved {out}")
    print(f"   Matrix: {matrix.shape}")
    print(f"   Products: {prod_df.shape}")
    print(f"   Content similarity: {sim.shape}")


if __name__ == "__main__":
    train()