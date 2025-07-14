import pandas as pd
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors


class Recommendations:
    def __init__(self, products_df, interactions_df=None):
        # Clean nulls
        products_df.fillna("", inplace=True)

        # Combine fields for text similarity
        products_df["combined_text"] = (
            products_df["product_name"].astype(str)
            + " "
            + products_df["description"].astype(str)
            + " "
            + products_df["category"].astype(str)
            + " "
            + products_df["subcategory"].astype(str)
            + " "
            + products_df["brand"].astype(str)
            + " "
            + products_df["material"].astype(str)
        )

        self.products_df = products_df
        self.product_indices = pd.Series(
            products_df.index, index=products_df["product_id"]
        )

        # TF-IDF product similarity
        self.tfidf = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = self.tfidf.fit_transform(products_df["combined_text"])
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)

        # Prepare collaborative filtering data if provided
        if interactions_df is not None:
            self._prepare_user_cf(interactions_df)
        else:
            self.user_cf_model = None

    def _prepare_user_cf(self, interactions_df):
        # Assign weights to interaction types
        interaction_weights = {
            "purchase": 5,
            "add_to_cart": 3,
            "wishlist": 2,
            "compare": 2,
            "view": 1,
            "search": 1,
        }

        interactions_df["score"] = (
            interactions_df["interaction_type"].map(interaction_weights).fillna(0)
        )

        # Sum weights for each (user, product)
        pivot = (
            interactions_df.groupby(["user_id", "product_id"])["score"]
            .sum()
            .unstack(fill_value=0)
        )

        self.user_item_matrix = pivot
        self.user_ids = list(pivot.index)
        self.product_ids = list(pivot.columns)

        # Fit k-NN model on user vectors
        self.user_cf_model = NearestNeighbors(metric="cosine", algorithm="brute")
        self.user_cf_model.fit(pivot)

    def get_user_to_user_recommendations(self, user_id, top_n=5):
        if self.user_cf_model is None:
            return "Collaborative filtering not initialized."

        if user_id not in self.user_item_matrix.index:
            return f"User ID {user_id} not found in interaction data."

        user_vector = self.user_item_matrix.loc[user_id].values.reshape(1, -1)
        distances, indices = self.user_cf_model.kneighbors(user_vector, n_neighbors=6)

        similar_users = self.user_item_matrix.index[
            indices.flatten()[1:]
        ]  # exclude self

        # Aggregate product scores from similar users
        recommendations = (
            self.user_item_matrix.loc[similar_users].sum().sort_values(ascending=False)
        )

        # Remove products the current user has already interacted with
        already_seen = self.user_item_matrix.loc[user_id]
        recommendations = recommendations[
            ~recommendations.index.isin(already_seen[already_seen > 0].index)
        ]

        # Get top N recommendations
        top_products = recommendations.head(top_n).index.tolist()

        return self.products_df[self.products_df["product_id"].isin(top_products)][
            [
                "product_id",
                "product_name",
                "category",
                "brand",
                "material",
                "price",
                "image_url",
                "product_url",
            ]
        ]

    def get_personalized_recommendations(self, user_id, top_n=5):
        if self.user_cf_model is None:
            return "Collaborative filtering not initialized."

        if user_id not in self.user_item_matrix.index:
            return f"User ID {user_id} not found in interaction data."

        user_scores = self.user_item_matrix.loc[user_id].copy()
        top_interactions = user_scores.sort_values(ascending=False)

        # Remove already seen and score 0
        top_interactions = top_interactions[top_interactions > 0]
        unseen_products = self.user_item_matrix.columns.difference(
            top_interactions.index
        )

        # If everything has been seen, fallback to product-based recommendations
        if len(unseen_products) == 0:
            return self.get_product_to_product_recommendations(
                top_interactions.index[0], num_recs=top_n
            )

        # Recommend similar products based on user preferences
        recommendations = []
        for prod_id in top_interactions.index:
            similar = self.get_product_to_product_recommendations(prod_id, num_recs=1)
            recommendations.extend(similar.to_dict(orient="records"))
            if len(recommendations) >= top_n:
                break

        return pd.DataFrame(recommendations[:top_n])

    def get_product_to_product_recommendations(self, product_id, num_recs=5):
        if product_id not in self.product_indices:
            return f"Product ID {product_id} not found."

        idx = self.product_indices[product_id]
        target = self.products_df.iloc[idx]

        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:]

        recommendations = []

        def filter_and_add(condition, count):
            nonlocal recommendations, sim_scores
            added = 0
            for i, _ in sim_scores:
                candidate = self.products_df.iloc[i]
                if (
                    condition(candidate)
                    and candidate["product_id"] != product_id
                    and candidate["product_id"]
                    not in [r["product_id"] for r in recommendations]
                ):
                    recommendations.append(candidate)
                    added += 1
                    if added == count:
                        break

        filter_and_add(
            lambda p: (
                p["category"] == target["category"]
                or p["subcategory"] == target["subcategory"]
            ),
            2,
        )

        filter_and_add(lambda p: p["brand"] == target["brand"], 2)
        filter_and_add(lambda p: p["material"] == target["material"], 1)

        return pd.DataFrame(recommendations)[
            [
                "product_id",
                "product_name",
                "category",
                "brand",
                "material",
                "price",
                "image_url",
                "product_url",
            ]
        ]

    def get_price_based_recommendations(self, product_id, top_n=5):
        if product_id not in self.product_indices:
            return f"Product ID {product_id} not found."

        target_price = self.products_df.loc[
            self.products_df["product_id"] == product_id, "price"
        ].values[0]

        price_df = self.products_df.copy()
        price_df["price_diff"] = (price_df["price"] - target_price).abs()
        price_df = price_df[price_df["product_id"] != product_id]
        closest = price_df.sort_values(by="price_diff").head(top_n)

        return closest[
            [
                "product_id",
                "product_name",
                "category",
                "brand",
                "material",
                "price",
                "image_url",
                "product_url",
            ]
        ]
