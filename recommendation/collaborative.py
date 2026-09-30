"""
User-based collaborative filtering using cosine similarity.
"""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

WEIGHTS = {"view": 1, "wishlist": 2, "addtocart": 3, "purchase": 5}


def build_user_item_matrix(interactions: pd.DataFrame) -> pd.DataFrame:
    df = interactions.copy()
    df["weight"] = df["interaction_type"].map(WEIGHTS).fillna(1)
    matrix = df.pivot_table(
        index="customer_id", columns="product_id",
        values="weight", aggfunc="sum", fill_value=0,
    )
    return matrix


def recommend_cf(user_id: int, matrix: pd.DataFrame, top_n: int = 10):
    if user_id not in matrix.index:
        return []

    user_vec = matrix.loc[[user_id]].values
    sims = cosine_similarity(user_vec, matrix.values)[0]
    sim_series = pd.Series(sims, index=matrix.index).drop(user_id, errors="ignore")

    # Keep top 50 similar users
    sim_series = sim_series.sort_values(ascending=False).head(50)

    if sim_series.sum() == 0:
        return []

    # Weighted sum of neighbours
    neighbour_scores = matrix.loc[sim_series.index].T.dot(sim_series)
    neighbour_scores = neighbour_scores / (sim_series.sum() + 1e-9)

    # Remove already-interacted
    already = matrix.loc[user_id][matrix.loc[user_id] > 0].index
    neighbour_scores = neighbour_scores.drop(already, errors="ignore")

    return neighbour_scores.sort_values(ascending=False).head(top_n).index.tolist()


if __name__ == "__main__":
    from recommendation.extract import load_interactions
    inter = load_interactions()
    matrix = build_user_item_matrix(inter)
    print("Matrix shape:", matrix.shape)

    sample_user = matrix.index[0]
    print(f"\nUser {sample_user} already interacted with:")
    print(matrix.loc[sample_user][matrix.loc[sample_user] > 0].head())

    recs = recommend_cf(sample_user, matrix, top_n=5)
    print(f"\nTop 5 CF recommendations for {sample_user}:")
    print(recs)