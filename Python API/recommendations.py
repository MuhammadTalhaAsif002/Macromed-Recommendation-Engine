import pandas as pd
from sqlalchemy import create_engine
import os
import sys

# Replace with your credentials
host = "localhost"
user = "root"
password = ""  # leave blank if no password
database = "macromed"

# Create engine
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# Load products table
products_df = pd.read_sql("SELECT * FROM products", engine)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from IPython.display import HTML
import pandas as pd


class Recommendations:
    def __init__(self, products_df):
        products_df.fillna("", inplace=True)
        products_df["combined_text"] = (
            products_df["product_name"]
            + " "
            + products_df["description"]
            + " "
            + products_df["category"]
            + " "
            + products_df["subcategory"]
            + " "
            + products_df["brand"]
            + " "
            + products_df["material"]
        )

        self.products_df = products_df
        self.product_indices = pd.Series(
            products_df.index, index=products_df["product_id"]
        )
        self.tfidf = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = self.tfidf.fit_transform(products_df["combined_text"])
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)

    def get_product_to_product_recommendations(self, product_id):
        if product_id not in self.product_indices:
            return f"Product ID {product_id} not found."

        idx = self.product_indices[product_id]
        target = self.products_df.iloc[idx]

        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:]  # remove self

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

        # 2 from same category or subcategory
        filter_and_add(
            lambda p: (
                p["category"] == target["category"]
                or p["subcategory"] == target["subcategory"]
            ),
            2,
        )

        # 2 from same brand
        filter_and_add(lambda p: p["brand"] == target["brand"], 2)

        # 1 from same material
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

    def display_products_with_images(self, df, max_items=5, notebook_only=True):
        df = df.copy().head(max_items)
        if notebook_only and not ("ipykernel" in sys.modules):
            print(df[["product_name", "price"]])  # fallback for .py script
            return

        html = "<table><tr>"
        for _, row in df.iterrows():
            html += f"""
            <td style="text-align:center; padding:10px">
                <a href="{row['product_url']}" target="_blank">
                    <img src="{row['image_url']}" width="120"><br>
                    <b>{row['product_name']}</b>
                </a><br>
                <i>{row['category']}</i><br>
                <span style="color:green; font-weight:bold;">${row['price']:.2f}</span><br>
            </td>
            """
        html += "</tr></table>"
        from IPython.display import HTML

        return HTML(html)
