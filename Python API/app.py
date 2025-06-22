from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine
import pandas as pd
from recommendations import Recommendations

# Flask app setup
app = Flask(__name__)
CORS(app)

# DB setup
host = "localhost"
user = "root"
password = ""
database = "macromed"
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# Load product data
products_df = pd.read_sql("SELECT * FROM products", engine)
rec = Recommendations(products_df)


@app.route("/api/recommend", methods=["GET"])
def recommend():
    product_id = request.args.get("product_id")
    rec_type = request.args.get("type", "content")  # content or price

    if not product_id:
        return jsonify({"error": "Missing product_id"}), 400

    try:
        product_id = int(product_id)
    except ValueError:
        return jsonify({"error": "Invalid product_id"}), 400

    # Get recommendations
    if rec_type == "content":
        df = rec.get_product_to_product_recommendations(product_id)
    elif rec_type == "price":
        df = rec.get_price_based_recommendations(product_id)
    else:
        return jsonify({"error": "Invalid type"}), 400

    if isinstance(df, str):
        return jsonify({"error": df}), 404

    return jsonify(df.to_dict(orient="records"))


# Run server
if __name__ == "__main__":
    app.run(debug=True, port=5000)
