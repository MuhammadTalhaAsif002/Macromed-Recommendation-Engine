import streamlit as st
import pandas as pd

# Load CSV
df = pd.read_csv("your_file.csv")  # replace with your CSV filename

st.title("🛍️ Surgical Products Catalog")

# Show first 10 products
for i, row in df.head(10).iterrows():
    st.image(row["Image"], width=200)
    st.subheader(row["Title"])
    st.write(f"**Category:** {row['Category']}")
    st.write(f"**Price:** ${row['Price']}")
    st.markdown("---")
