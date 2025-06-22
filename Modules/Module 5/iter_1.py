import streamlit as st
import pandas as pd

# Load user and tool data
users_df = pd.read_excel(
    r"C:/Users/Dell/Desktop/Recommendation Systems/Macromed-Recommendation-Engine/Generated Data/surgical_tool_recommendation_users (5).xlsx"
)
tools_df = pd.read_excel(
    r"C:/Users/Dell/Desktop/Recommendation Systems/Macromed-Recommendation-Engine/Generated Data/surgical_tool_prices (5).xlsx"
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

# First, ask for budget selection
budget = st.selectbox("💳 Select your Budget Range", ["Low", "Medium", "High"])

# Show tools within the selected budget
tools_in_budget = [
    tool for tool, price in tool_price_dict.items() if budget_price_map[budget](price)
]

if tools_in_budget:
    selected_tools = st.multiselect(
        "🧰 Select tools based on your budget", tools_in_budget
    )
else:
    st.warning(f"No tools found in the {budget} budget range.")

st.divider()

# After selecting tools, give the option to choose a user or general recommendation
recommendation_type = st.radio(
    "🎯 Choose recommendation type",
    (
        "Personalized Recommendation (based on user history)",
        "General Recommendation (based on budget)",
    ),
)

# If the user chooses personalized recommendation
if recommendation_type == "Personalized Recommendation (based on user history)":
    user_id = st.selectbox(
        "🧑‍⚕️ Select a User ID for personalized recommendations",
        users_df["userID"].tolist(),
    )

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
        st.code(
            ", ".join(user_row["previousPurchases"].split("|")), language="markdown"
        )

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
            st.warning(
                "✅ All available tools in your budget range are already purchased!"
            )

# If the user chooses general recommendation based on selected tools
else:
    st.subheader("🎯 General Recommendations")
    if selected_tools:
        st.markdown("**You have selected the following tools:**")
        st.code(", ".join(selected_tools), language="markdown")
        st.markdown(
            "**Based on your budget, here are some other tools you might be interested in:**"
        )
        general_recs = [
            tool
            for tool, price in tool_price_dict.items()
            if budget_price_map[budget](price) and tool not in selected_tools
        ]
        if general_recs:
            for i, tool in enumerate(general_recs, 1):
                price = tool_price_dict[tool]
                st.markdown(f"**{i}. {tool}** 💰 Price: ${price}")
        else:
            st.warning("No other tools available in your budget.")
    else:
        st.warning("No valid recommendations.")
