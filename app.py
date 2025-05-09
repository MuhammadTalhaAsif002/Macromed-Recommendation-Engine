import streamlit as st
import pandas as pd
import plotly.express as px
from itertools import cycle
import random
import requests
from PIL import Image
from io import BytesIO

# Load the data
@st.cache_data
def load_data():
    # Main products
    df = pd.read_csv(r'E:\FYP\fyp_reco\hybrid_recommendations.csv')
    df['Has_Image'] = df['Has_Image'].astype(bool)
    df['Dimensions'] = df['Dimensions'].fillna('Not specified')
    df['Image'] = df['Image'].replace('Missing_URL', '')
    
    # Top products with sales data
    top_df = pd.read_csv(r'E:\FYP\fyp_reco\top_products_per_sales.csv')
    top_df['Image'] = top_df['Image'].fillna('')
    
    # Merge datasets (simulating recommendations)
    df['Popularity_Score'] = df['Discount_Percentage'] * 0.6 + (df['Price'] - df['discounted_price']) * 0.4
    top_df['Popularity_Score'] = top_df['sales_count'] * 0.7 + top_df['ratings'] * 0.3
    
    return df, top_df

@st.cache_data(ttl=3600)
def is_valid_image(url):
    """Check if an image URL is valid and accessible"""
    if not url or pd.isna(url) or url.strip() == '':
        return False
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type.lower():
                return True
        return False
    except:
        return False

def get_valid_products(df, count):
    """Return products with valid images"""
    valid_products = []
    for _, product in df.iterrows():
        if is_valid_image(product['Image']):
            valid_products.append(product)
            if len(valid_products) >= count:
                break
    return pd.DataFrame(valid_products)

df, top_df = load_data()

# Custom CSS for professional look
st.markdown("""
<style>
    :root {
        --primary: #2b5876;
        --secondary: #4e4376;
        --accent: #e63946;
        --light: #f8f9fa;
        --dark: #212529;
    }
    
    .main {
        max-width: 1400px;
        padding-top: 1.5rem;
    }
    
    .header {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .product-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        height: 100%;
        position: relative;
        background: white;
    }
    
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        border-color: var(--accent);
    }
    
    .badge {
        position: absolute;
        top: 10px;
        right: 10px;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
        color: white;
        z-index: 2;
    }
    
    .hot-badge {
        background: var(--accent);
    }
    
    .new-badge {
        background: #4caf50;
    }
    
    .top-badge {
        background: #ff9800;
    }
    
    .price {
        font-weight: bold;
        margin: 10px 0;
    }
    
    .original-price {
        text-decoration: line-through;
        color: #999;
        font-size: 14px;
    }
    
    .discounted-price {
        color: var(--accent);
        font-size: 18px;
        font-weight: 700;
    }
    
    .discount-badge {
        background-color: var(--accent);
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        margin-left: 5px;
    }
    
    .category-tag {
        background-color: #f0f8ff;
        color: var(--primary);
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 12px;
        display: inline-block;
        margin-bottom: 8px;
    }
    
    .section-header {
        border-left: 5px solid var(--accent);
        padding-left: 15px;
        margin: 2rem 0 1rem;
        color: var(--primary);
    }
    
    .trending-section {
        background: linear-gradient(to right, #fff8f8, #fff);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 2rem 0;
        border: 1px solid #ffecec;
    }
    
    .recommendation-section {
        background: linear-gradient(to right, #f8faff, #fff);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 2rem 0;
        border: 1px solid #e6ecff;
    }
    
    .stButton>button {
        background-color: var(--primary);
        color: white;
        border-radius: 6px;
        border: none;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: var(--secondary);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .stSelectbox>div>div>div {
        padding: 8px 12px;
    }
    
    .stSlider>div>div>div {
        background-color: var(--primary);
    }
    
    /* Custom scrollbar for trending products */
    .horizontal-scroll {
        display: flex;
        overflow-x: auto;
        padding-bottom: 15px;
        scrollbar-width: thin;
    }
    
    .horizontal-scroll::-webkit-scrollbar {
        height: 6px;
    }
    
    .horizontal-scroll::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .horizontal-scroll::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 10px;
    }
    
    .horizontal-scroll::-webkit-scrollbar-thumb:hover {
        background: var(--secondary);
    }
    
    .product-card-horizontal {
        min-width: 220px;
        margin-right: 15px;
    }
    
    /* Rating stars */
    .rating {
        display: inline-flex;
        margin-top: 5px;
    }
    
    .star {
        color: #ffc107;
        font-size: 14px;
        margin-right: 2px;
    }
    
    .review-count {
        font-size: 12px;
        color: #6c757d;
        margin-left: 5px;
    }
    
    .no-image {
        background-color: #f5f5f5;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 180px;
        border-radius: 5px;
        color: #999;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Header section
st.markdown("""
<div class="header">
    <h1 style="margin-bottom: 0.5rem;">SurgicalMart Pro</h1>
    <p style="margin-top: 0; opacity: 0.9;">Premium Surgical Instruments & Medical Supplies</p>
</div>
""", unsafe_allow_html=True)

# Navigation
st.markdown("""
<div style="display: flex; justify-content: space-between; margin-bottom: 1.5rem; border-bottom: 1px solid #eee; padding-bottom: 1rem;">
    <div style="display: flex; gap: 20px;">
        <a href="#personalized" style="text-decoration: none; color: var(--primary); font-weight: 500;">Recommended</a>
        <a href="#trending" style="text-decoration: none; color: var(--primary); font-weight: 500;">Trending</a>
        <a href="#shop" style="text-decoration: none; color: var(--primary); font-weight: 500;">Shop All</a>
        <a href="#categories" style="text-decoration: none; color: var(--primary); font-weight: 500;">Categories</a>
    </div>
    <div>
        <input type="text" placeholder="Search products..." style="padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; min-width: 250px;">
    </div>
</div>
""", unsafe_allow_html=True)

# User type selection
st.markdown('<a name="personalized"></a>', unsafe_allow_html=True)
st.subheader("👋 Personalized Recommendations")
user_type = st.radio(
    "I am a:",
    ["Hospital Purchaser", "Surgeon", "Clinic Administrator", "Just Browsing"],
    horizontal=True,
    key="user_type"
)

# Get recommendations based on user type with valid images
if user_type == "Hospital Purchaser":
    rec_df = get_valid_products(df[df['Price'] > 50].sort_values('Popularity_Score', ascending=False), 6)
elif user_type == "Surgeon":
    rec_df = get_valid_products(df[df['Category'].str.contains('Needle|Scalpel|Scissors')].sort_values('Popularity_Score', ascending=False), 6)
elif user_type == "Clinic Administrator":
    rec_df = get_valid_products(df[df['Price'] < 50].sort_values('Popularity_Score', ascending=False), 6)
else:
    rec_df = get_valid_products(df.sample(frac=1), 6)  # Randomize for "Just Browsing"

# Display personalized recommendations
if not rec_df.empty:
    cols = st.columns(3)
    for idx, (_, product) in enumerate(rec_df.iterrows()):
        with cols[idx % 3]:
            discount_percent = int(round(product['Discount_Percentage']))
            badge = ""
            if product['Popularity_Score'] > df['Popularity_Score'].quantile(0.8):
                badge = '<span class="badge hot-badge">HOT</span>'
            elif product['Discount_Percentage'] > 40:
                badge = '<span class="badge new-badge">SALE</span>'
                
            st.markdown(f"""
            <div class="product-card">
                {badge}
                <div style="position: relative; height: 180px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                    <img src="{product['Image']}" style="max-width: 100%; max-height: 180px; object-fit: contain; border-radius: 5px;" onerror="this.style.display='none'; this.parentNode.innerHTML='<div class=\\'no-image\\'>Image not available</div>';">
                </div>
                <div class="category-tag">{product['Category']}</div>
                <h4 style="margin: 5px 0 10px; font-size: 16px; line-height: 1.3;">{product['Title'][:50]}{'...' if len(product['Title']) > 50 else ''}</h4>
                <div class="price">
                    <span class="original-price">${product['Price']:.2f}</span>
                    <span class="discounted-price">${product['discounted_price']:.2f}</span>
                    <span class="discount-badge">{discount_percent}% OFF</span>
                </div>
                {f'<div style="font-size: 12px; color: #666; margin: 5px 0;">Size: {product["Dimensions"]}</div>' if str(product["Dimensions"]) != "Not specified" else ""}
                <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                    <a href="{product['Title_URL']}" target="_blank" style="text-decoration: none; color: var(--primary); font-size: 14px; font-weight: 500;">Details</a>
                    <button onclick="window.open('{product['Type_URL']}', '_blank')" style="background: var(--primary); color: white; border: none; padding: 5px 15px; border-radius: 4px; font-size: 14px; cursor: pointer;">Add to Cart</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("No products available with valid images for the selected category.")

# Trending Products Section
st.markdown('<a name="trending"></a>', unsafe_allow_html=True)
st.markdown("""
<div class="trending-section">
    <h3 style="margin-top: 0; color: var(--primary);">🔥 Top Selling Products</h3>
    <p style="margin-bottom: 0; color: #666;">Most popular items based on sales data</p>
</div>
""", unsafe_allow_html=True)

# Display trending products in a horizontal scroll
valid_top_products = get_valid_products(top_df.sort_values('Popularity_Score', ascending=False), 10)

if not valid_top_products.empty:
    st.markdown("""
    <div class="horizontal-scroll">
    """, unsafe_allow_html=True)

    for idx, (_, product) in enumerate(valid_top_products.iterrows()):
        discount_percent = int(round((product['Price'] - product['Price1']) / product['Price'] * 100))
        
        # Generate star rating display
        stars = int(round(product['ratings']))
        star_html = ''.join(['<span class="star">★</span>' for _ in range(stars)])
        if stars < 5:
            star_html += ''.join(['<span class="star" style="color: #ddd;">★</span>' for _ in range(5 - stars)])
        
        st.markdown(f"""
        <div class="product-card product-card-horizontal">
            <span class="badge top-badge">TOP {idx+1}</span>
            <div style="position: relative; height: 120px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                <img src="{product['Image']}" style="max-width: 100%; max-height: 120px; object-fit: contain; border-radius: 5px;" onerror="this.style.display='none'; this.parentNode.innerHTML='<div class=\\'no-image\\' style=\\'height:120px\\'>Image not available</div>';">
            </div>
            <div class="category-tag">{product['Category']}</div>
            <h4 style="margin: 5px 0 8px; font-size: 15px; line-height: 1.3;">{product['Title'][:40]}{'...' if len(product['Title']) > 40 else ''}</h4>
            <div class="price">
                <span class="original-price">${product['Price']:.2f}</span>
                <span class="discounted-price">${product['Price1']:.2f}</span>
                <span class="discount-badge">{discount_percent}% OFF</span>
            </div>
            <div class="rating">
                {star_html}
                <span class="review-count">({product['review_counts']})</span>
            </div>
            <div style="font-size: 12px; color: #666; margin: 5px 0;">{product['sales_count']} sold</div>
            <button onclick="window.open('{product['Image'].replace('https://surgicalmart.com/wp-content/uploads/', 'https://surgicalmart.com/shop/').rsplit('/', 1)[0]}', '_blank')" style="width: 100%; background: var(--primary); color: white; border: none; padding: 5px 0; border-radius: 4px; font-size: 14px; cursor: pointer; margin-top: 10px;">View Details</button>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("No trending products available with valid images.")

# Category-based browsing
st.markdown('<a name="categories"></a>', unsafe_allow_html=True)
st.subheader("🛍️ Shop by Category")

categories = df['Category'].unique()
category_cols = st.columns(4)
for idx, category in enumerate(categories[:4]):
    with category_cols[idx]:
        # Get a valid product for this category
        category_products = df[df['Category'] == category]
        valid_category_products = get_valid_products(category_products, 1)
        
        if not valid_category_products.empty:
            product = valid_category_products.iloc[0]
            st.markdown(f"""
            <div style="text-align: center; cursor: pointer; padding: 15px; border-radius: 8px; background: white; border: 1px solid #eee; transition: all 0.3s;" 
                 onMouseOver="this.style.boxShadow='0 5px 15px rgba(0,0,0,0.1)'; this.style.borderColor='var(--accent)';" 
                 onMouseOut="this.style.boxShadow='none'; this.style.borderColor='#eee';"
                 onclick="window.open('{product['Title_URL']}', '_blank')">
                <img src="{product['Image']}" style="width: 100%; height: 100px; object-fit: contain; margin-bottom: 10px;" onerror="this.style.display='none'; this.parentNode.innerHTML='<div class=\\'no-image\\' style=\\'height:100px\\'>No Image</div>';">
                <p style="font-weight: bold; margin: 0; color: var(--primary);">{category}</p>
                <p style="margin: 0; font-size: 12px; color: #666;">{len(df[df['Category'] == category])} products</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; border-radius: 8px; background: white; border: 1px solid #eee;">
                <div class="no-image" style="height:100px; margin-bottom:10px;">No Image</div>
                <p style="font-weight: bold; margin: 0; color: var(--primary);">{category}</p>
                <p style="margin: 0; font-size: 12px; color: #666;">{len(df[df['Category'] == category])} products</p>
            </div>
            """, unsafe_allow_html=True)

# All Products Section with Filters
st.markdown('<a name="shop"></a>', unsafe_allow_html=True)
st.subheader("📦 Browse All Products")

# Filters
col1, col2, col3, col4 = st.columns(4)
with col1:
    category_filter = st.selectbox("Category", ["All"] + sorted(list(df['Category'].unique())), key="category_filter")
with col2:
    price_range = st.slider(
        "Price Range ($)",
        min_value=int(df['discounted_price'].min()),
        max_value=int(df['discounted_price'].max()) + 1,
        value=(int(df['discounted_price'].min()), int(df['discounted_price'].max())),
        key="price_filter"
    )
with col3:
    sort_option = st.selectbox(
        "Sort By",
        ["Recommended", "Price: Low to High", "Price: High to Low", "Discount %", "Popularity"],
        key="sort_filter"
    )
with col4:
    items_per_page = st.selectbox(
        "Items per page",
        [6, 12, 24],
        key="pagination"
    )

# Apply filters
filtered_df = df.copy()
if category_filter != "All":
    filtered_df = filtered_df[filtered_df['Category'] == category_filter]
filtered_df = filtered_df[
    (filtered_df['discounted_price'] >= price_range[0]) & 
    (filtered_df['discounted_price'] <= price_range[1])
]

if sort_option == "Price: Low to High":
    filtered_df = filtered_df.sort_values('discounted_price', ascending=True)
elif sort_option == "Price: High to Low":
    filtered_df = filtered_df.sort_values('discounted_price', ascending=False)
elif sort_option == "Discount %":
    filtered_df = filtered_df.sort_values('Discount_Percentage', ascending=False)
elif sort_option == "Popularity":
    filtered_df = filtered_df.sort_values('Popularity_Score', ascending=False)
else:
    filtered_df = filtered_df.sample(frac=1)  # Randomize for "Recommended"

# Get only products with valid images
filtered_df = get_valid_products(filtered_df, len(filtered_df))

# Pagination
total_pages = (len(filtered_df) // items_per_page) + (1 if len(filtered_df) % items_per_page else 0)
if total_pages > 1:
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, key="page_number")
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    paginated_df = filtered_df.iloc[start_idx:end_idx]
else:
    paginated_df = filtered_df

# Display all filtered products
if not paginated_df.empty:
    cols = st.columns(3)
    for idx, (_, product) in enumerate(paginated_df.iterrows()):
        with cols[idx % 3]:
            discount_percent = int(round(product['Discount_Percentage']))
            badge = ""
            if product['Popularity_Score'] > df['Popularity_Score'].quantile(0.8):
                badge = '<span class="badge hot-badge">HOT</span>'
            elif product['Discount_Percentage'] > 40:
                badge = '<span class="badge new-badge">SALE</span>'
                
            st.markdown(f"""
            <div class="product-card">
                {badge}
                <div style="position: relative; height: 180px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                    <img src="{product['Image']}" style="max-width: 100%; max-height: 180px; object-fit: contain; border-radius: 5px;" onerror="this.style.display='none'; this.parentNode.innerHTML='<div class=\\'no-image\\'>Image not available</div>';">
                </div>
                <div class="category-tag">{product['Category']}</div>
                <h4 style="margin: 5px 0 10px; font-size: 16px; line-height: 1.3;">{product['Title'][:50]}{'...' if len(product['Title']) > 50 else ''}</h4>
                <div class="price">
                    <span class="original-price">${product['Price']:.2f}</span>
                    <span class="discounted-price">${product['discounted_price']:.2f}</span>
                    <span class="discount-badge">{discount_percent}% OFF</span>
                </div>
                {f'<div style="font-size: 12px; color: #666; margin: 5px 0;">Size: {product["Dimensions"]}</div>' if str(product["Dimensions"]) != "Not specified" else ""}
                <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                    <a href="{product['Title_URL']}" target="_blank" style="text-decoration: none; color: var(--primary); font-size: 14px; font-weight: 500;">Details</a>
                    <button onclick="window.open('{product['Type_URL']}', '_blank')" style="background: var(--primary); color: white; border: none; padding: 5px 15px; border-radius: 4px; font-size: 14px; cursor: pointer;">Add to Cart</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("No products match your filters.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <div style="display: flex; justify-content: center; gap: 20px; margin-bottom: 1rem;">
        <a href="#" style="text-decoration: none; color: var(--primary);">About Us</a>
        <a href="#" style="text-decoration: none; color: var(--primary);">Contact</a>
        <a href="#" style="text-decoration: none; color: var(--primary);">Shipping Policy</a>
        <a href="#" style="text-decoration: none; color: var(--primary);">Returns</a>
    </div>
    <p style="color: #6c757d; margin: 0;">© 2023 SurgicalMart Pro. All rights reserved.</p>
    <p style="color: #6c757d; margin: 0;">Professional surgical equipment for medical practitioners</p>
</div>
""", unsafe_allow_html=True)