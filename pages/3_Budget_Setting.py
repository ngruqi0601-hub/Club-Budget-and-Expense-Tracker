import streamlit as st
from database import add_budget, get_budgets,get_expenses
st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #F8F5FF !important;
}

/* Headings */
.stApp h1,
.stApp h2,
.stApp h3 {
    color: #8156C5 !important;
    font-weight: bold;
}

/* Paragraphs */
.stApp [data-testid="stMarkdownContainer"] p {
    color: #76658F;
    line-height: 1.6;
}

/* Cards */
div[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #E5D9F5;
    border-radius: 15px;
    padding: 18px;
    box-shadow: 0 4px 12px rgba(129, 86, 197, 0.12);
}

/* Metric labels */
div[data-testid="stMetricLabel"] {
    color: #60418F !important;
}

/* Number input */
.stNumberInput input {
    background-color: #F3EDFF !important;
    color: #60418F !important;
    border-radius: 12px !important;
}

/* Buttons */
.stButton > button {
    width: 100%;
    padding: 12px;
    background-color: #A080D5 !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: bold;
    font-size: 16px !important;
    box-shadow: 0 4px 8px rgba(129, 86, 197, 0.2);
    transition: 0.3s ease;
}

/* Button text */
.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: white !important;
}

.stButton > button:hover {
    background-color: #8156C5 !important;
    transform: translateY(-2px);
}

/* Divider */
.stApp hr {
    border-color: #D8C5F2 !important;
}

</style>
""", unsafe_allow_html=True)
st.title("Budget Setting")

st.subheader("Set Category Budget")

category = st.selectbox(
    "Select Category",
    [
        "Food",
        "Transportation",
        "Equipment",
        "Accommodation",
        "Workshop Materials",
        "Utilities",
        "Competition Fees",
        "Membership Activities",
        "Others"
    ]
)

budget_limit = st.number_input(
    "Enter Budget Limit (RM)",
    min_value=0.0,
    step=10.0
)

if st.button("Submit Budget", key="submit_budget"):
    if budget_limit <= 0:
        st.warning("Please enter a valid budget limit.")
    else:
        add_budget(category, budget_limit)
        st.success(f"Budget for {category} submitted successfully!")
st.divider()
st.subheader("Budget Overview")

budgets = get_budgets()
expenses = get_expenses()
category_totals = {}

for expense in expenses:
    category_name = expense[3]
    amount = expense[2]

    if category_name not in category_totals:
        category_totals[category_name] = 0

    category_totals[category_name] += amount
if budgets:
    for budget in budgets:
        budget_id = budget[0]
        category_name = budget[1]
        budget_limit = budget[2]
        actual_spending = category_totals.get(category_name, 0)
        remaining = budget_limit - actual_spending
        st.markdown(f"###{category_name}")
        col1, col2, col3 = st.columns(3)

        col1.metric("Budget", f"RM {budget_limit:.2f}")
        col2.metric("Spent", f"RM {actual_spending:.2f}")
        col3.metric("Remaining", f"RM {remaining:.2f}")
        spending_ratio=actual_spending/budget_limit 
        st.progress(min(spending_ratio,1.0))
        st.write(f"Budget used:{spending_ratio*100:.1f}%")
        if spending_ratio >= 1:
            st.error("Budget exceeded!")

        elif spending_ratio >= 0.8:
            st.warning("You are approaching your budget limit!")

        else:
            st.success("Spending is within the budget.")
            st.divider()
    else:
        st.info("No category budgets have been set yet.")
    