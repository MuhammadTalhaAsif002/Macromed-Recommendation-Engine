import streamlit as st
import pandas as pd

# Load user and tool data
users_df = pd.read_excel(
    "C:/Users/Dell/Desktop/Recommendation Systems/Macromed-Recommendation-Engine/Generated Data/surgical_tool_recommendation_users (5).xlsx"
)
tools_df = pd.read_excel(
    "C:/Users/Dell/Desktop/Recommendation Systems/Macromed-Recommendation-Engine/Generated Data/surgical_tool_prices (5).xlsx"
)


# Budget filter logic
budget_price_map = {
    "Low": lambda p: p <= 50,
    "Medium": lambda p: 51 <= p <= 100,
    "High": lambda p: p > 100,
}

# Tool-price lookup
tool_price_dict = tools_df.set_index("toolName")["priceUSD"].to_dict()


# Recommendation function
def recommend_tools_for_user(user_row, top_k=3):
    budget = user_row["budgetRange"]
    purchased = user_row["previousPurchases"].split("|")

    tools_in_budget = [
        tool
        for tool, price in tool_price_dict.items()
        if budget_price_map[budget](price)
    ]

    recommendations = [tool for tool in tools_in_budget if tool not in purchased]
    return recommendations[:top_k]


# --- Streamlit UI ---
st.set_page_config(
    page_title="🛠️ Surgical Tool Recommender (Budget Based)", layout="centered"
)
st.markdown(
    "<h1 style='text-align: center;'>🔧 Surgical Tool Recommendation System (Budget Based)</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "##### Get personalized tool suggestions based on budget and previous purchases."
)

st.divider()

# Dropdown to select user ID
user_id = st.selectbox("🧑‍⚕️ Select a User ID", users_df["userID"].tolist())

if user_id:
    user_row = users_df[users_df["userID"] == user_id].iloc[0]

    st.subheader("👤 Surgeon Profile")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🆔 ID", user_row["userID"])
    with col2:
        st.metric("🔬 Specialty", user_row["specialization"])
    with col3:
        st.metric("💼 Experience", user_row["experienceLevel"])

    st.markdown(f"**💳 Budget Preference:** `{user_row['budgetRange']}`")

    st.markdown("**🧾 Previous Purchases:**")
    st.code(", ".join(user_row["previousPurchases"].split("|")), language="markdown")

    st.subheader("🎯 Recommended Tools")
    recs = recommend_tools_for_user(user_row)

    if recs:
        for i, tool in enumerate(recs, 1):
            price = tool_price_dict[tool]
            with st.container():
                st.markdown(
                    f"""
                    <div style='padding: 10px; background-color: #f9f9f9; border-radius: 10px; margin-bottom: 10px;'>
                        <h4>{i}. {tool}</h4>
                        <p>💰 <strong>Price:</strong> ${price}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.warning("✅ All available tools in your budget range are already purchased!")
