"""
Content-based filtering using TF-IDF over product names + category.
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_content_model(products: pd.DataFrame):
    df = products.copy()
    df["text"] = (
        df["product_name"].astype(str)
        + " cat_" + df["category_id"].astype(str)
    )
    tfidf = TfidfVectorizer(stop_words="english", max_features=5000, ngram_range=(1, 2))
    mat = tfidf.fit_transform(df["text"])
    sim = cosine_similarity(mat)
    return df.reset_index(drop=True), sim


def recommend_content(user_history_ids, products, sim, top_n: int = 10):
    if not user_history_ids:
        return []

    idx = products.index[products["product_id"].isin(user_history_ids)].tolist()
    if not idx:
        return []

    scores = sim[idx].mean(axis=0)
    ranked = pd.Series(scores, index=products["product_id"]).sort_values(ascending=False)
    ranked = ranked.drop(user_history_ids, errors="ignore")
    return ranked.head(top_n).index.tolist()


if __name__ == "__main__":
    from recommendation.extract import load_products, load_interactions

    products = load_products()
    prods_df, sim = build_content_model(products)
    print("Sim matrix:", sim.shape)

    # Simulate a user's history with first 5 products
    sample_history = prods_df["product_id"].head(5).tolist()
    recs = recommend_content(sample_history, prods_df, sim, top_n=5)
    print("Content-based recs for history:", sample_history)
    print("Recommended:", recs)