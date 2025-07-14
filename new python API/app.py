from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine
import pandas as pd
from recommendations import Recommendations

# Flask app setup
app = Flask(__name__)
CORS(app)

# PostgreSQL DB credentials
host = "localhost"
port = 5432
user = "postgres"
password = "1234"
database = "Macromed"

# Create SQLAlchemy engine
engine = create_engine(
    f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
)

# Load products and interactions tables
try:
    products_df = pd.read_sql("SELECT * FROM products", engine)
    interactions_df = pd.read_sql("SELECT * FROM interactions", engine)
except Exception as e:
    print(f"❌ Error loading tables: {e}")
    products_df = pd.DataFrame()
    interactions_df = pd.DataFrame()

# Initialize recommendation engine
rec = Recommendations(products_df, interactions_df)


@app.route("/api/recommend", methods=["GET"])
def recommend():
    rec_type = request.args.get("type", "content")  # content, price, cf, personalized

    # Personalized Recommendation (user’s own interaction history)
    if rec_type == "personalized":
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({"error": "Invalid user_id"}), 400

        df = rec.get_personalized_recommendations(user_id)
        if isinstance(df, str):
            return jsonify({"error": df}), 404
        return jsonify(df.to_dict(orient="records"))

    # Collaborative Filtering (user-to-user)
    elif rec_type == "cf":
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({"error": "Invalid user_id"}), 400

        df = rec.get_user_to_user_recommendations(user_id)
        if isinstance(df, str):
            return jsonify({"error": df}), 404
        return jsonify(df.to_dict(orient="records"))

    # Content-based or price-based
    else:
        product_id = request.args.get("product_id")
        if not product_id:
            return jsonify({"error": "Missing product_id"}), 400
        try:
            product_id = int(product_id)
        except ValueError:
            return jsonify({"error": "Invalid product_id"}), 400

        if rec_type == "content":
            df = rec.get_product_to_product_recommendations(product_id)
        elif rec_type == "price":
            df = rec.get_price_based_recommendations(product_id)
        else:
            return jsonify({"error": "Invalid type"}), 400

        if isinstance(df, str):
            return jsonify({"error": df}), 404
        return jsonify(df.to_dict(orient="records"))


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify(
        {
            "status": "ok",
            "products_loaded": len(products_df),
            "interactions_loaded": len(interactions_df),
        }
    )


# Run the Flask server
if __name__ == "__main__":
    app.run(debug=True, port=5000)
