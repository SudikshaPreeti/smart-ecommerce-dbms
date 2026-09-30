"""
Hybrid recommender = weighted blend of collaborative + content-based.
"""
from recommendation.extract import load_interactions, load_products
from recommendation.collaborative import build_user_item_matrix, recommend_cf
from recommendation.content_based import build_content_model, recommend_content


def get_hybrid_recommendations(user_id: int, alpha: float = 0.6, top_n: int = 10):
    """
    alpha = weight for CF (1-alpha = weight for content-based).
    """
    interactions = load_interactions()
    products     = load_products()

    # --- CF side ---
    matrix = build_user_item_matrix(interactions)
    cf_items = recommend_cf(user_id, matrix, top_n=30)

    # --- Content side ---
    user_hist = interactions.loc[
        interactions.customer_id == user_id, "product_id"
    ].unique().tolist()

    prod_df, sim = build_content_model(products)
    cb_items = recommend_content(user_hist, prod_df, sim, top_n=30)

    # --- Merge with rank-based score ---
    scores = {}
    for rank, pid in enumerate(cf_items):
        scores[pid] = scores.get(pid, 0) + alpha * (1 / (rank + 1))
    for rank, pid in enumerate(cb_items):
        scores[pid] = scores.get(pid, 0) + (1 - alpha) * (1 / (rank + 1))

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [pid for pid, _ in ranked]


if __name__ == "__main__":
    from recommendation.extract import load_interactions
    inter = load_interactions()
    user = inter["customer_id"].value_counts().index[0]  # most active user
    print(f"Top recommendations for user {user}:")
    recs = get_hybrid_recommendations(user, alpha=0.6, top_n=10)
    print(recs)