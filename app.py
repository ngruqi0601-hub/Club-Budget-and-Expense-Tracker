
import streamlit as st
import pandas as pd
from navigation import show_finance_sidebar
from storage import get_supabase_client
from database import (
    get_total_club_budget,
    get_total_club_expenses,
    get_remaining_club_budget,
    get_category_expense_totals,
    get_club_budgets
)
#1. login check
if not st.session_state.get("logged_in", False):
    st.warning("Please log in to access this page.")
    st.switch_page("pages/0_Account.py")
    st.stop()


# 2. PAGE CONFIGURATION
st.set_page_config(
    page_title="Club Budget Tracker",
    page_icon="💰",
    layout="wide"
)
club_name=st.session_state.get("selected_club_name","Selected_Club")
st.title(f"💰 {club_name} Budget Setting")


show_finance_sidebar()



# 3. CHECK SELECTED CLUB


club_id = st.session_state.get("selected_club_id")

if club_id is None:
    st.warning("Please select a club first.")

    if st.button("Select Club"):
        st.switch_page("pages/5_Club_Navigation.py")

    st.stop()



# 4. CUSTOM CSS


st.markdown("""
<style>
[data-testid="stSidebarNav"] {
    display: none;
}

.stApp {
    background-color: #F8F5FF!important;
}

h1 {
    color: #8156C5!important;
}

h2, h3 {
    color: #A05ACB!important;
}

/* First dashboard card */
div[data-testid="stHorizontalBlock"] > div:nth-child(1)
[data-testid="stMetric"] {
    background-color: #E9E1FF;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
}

/* Second dashboard card */
div[data-testid="stHorizontalBlock"] > div:nth-child(2)
[data-testid="stMetric"] {
    background-color: #FFE4EB;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
}

/* Third dashboard card */
div[data-testid="stHorizontalBlock"] > div:nth-child(3)
[data-testid="stMetric"] {
    background-color: #DDF5EE;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    transition: 0.3s ease;
}

.stButton > button {
    width: 100% !important;
    background-color: #8156C5 !important;
    color: white !important;
    border-radius: 12px;
    border: none;
    padding: 10px 25px;
    font-weight: bold;
    font-size: 20px !important;
    transition: all 0.3s ease;
}

.stButton > button p {
    font-size: 20px !important;
}

.stButton > button:hover {
    background-color: #946FD0 !important;
    color: white !important;
    transform: translateY(-3px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.stApp h1, .stApp h2, .stApp h3 {
    margin-bottom: 20px;
}

.stApp [data-testid="stMarkdownContainer"] p {
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)



# 5. DASHBOARD HEADER


club_name = st.session_state.get(
    "selected_club_name",
    "Selected Club"
)

st.title("Club Budget and Expense Tracker")
st.write("Welcome to our club financial management system!")

st.divider()

st.subheader(f"📊 {club_name} Dashboard")

if st.button("🔄 Refresh Dashboard"):
    st.rerun()



# 6. OVERALL FINANCIAL SUMMARY


total_budget = get_total_club_budget(club_id)
total_expenses = get_total_club_expenses(club_id)
remaining_budget = get_remaining_club_budget(club_id)

if total_budget > 0:
    remaining_percentage = (
        remaining_budget / total_budget
    ) * 100
else:
    remaining_percentage = 0


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Budget",
        f"RM {total_budget:.2f}"
    )

with col2:
    st.metric(
        "Total Expenses",
        f"RM {total_expenses:.2f}"
    )

with col3:
    st.metric(
        "Remaining Budget",
        f"RM {remaining_budget:.2f}",
        delta=f"{remaining_percentage:.1f}% remaining"
    )


# ==================================
# 7. CLUB BUDGET USAGE
# ==================================

st.divider()
st.subheader("Club Budget Usage")

if total_budget > 0:

    usage = total_expenses / total_budget

    st.progress(min(usage, 1.0))
    st.write(f"Budget Used: {usage * 100:.1f}%")

    if usage > 1:
        st.error(
            "Club expenses have exceeded the total budget!"
        )

    elif usage >= 0.8:
        st.warning(
            "Attention! The club has used at least 80% of its budget."
        )

    else:
        st.success(
            "Club spending is within a healthy range."
        )

else:
    st.info("No club budget has been set yet.")


# ==================================
# 8. CATEGORY BUDGET ANALYSIS
# ==================================

st.divider()
st.subheader("Category Budget Analysis")

budgets = get_club_budgets(club_id)
category_expenses = get_category_expense_totals(club_id)

budget_dict = {
    budget[1]: budget[2]
    for budget in budgets
}

expense_dict = {
    category: amount
    for category, amount in category_expenses
}


# ==================================
# 9. APPROVED EXPENSES PIE CHART
# ==================================

st.write("**Approved Expenses Distribution**")

if category_expenses:

    chart_data = pd.DataFrame(
        category_expenses,
        columns=["Category", "Amount"]
    )

    st.vega_lite_chart(
        chart_data,
        {
            "mark": {
                "type": "arc",
                "innerRadius": 50
            },
            "encoding": {
                "theta": {
                    "field": "Amount",
                    "type": "quantitative"
                },
                "color": {
                    "field": "Category",
                    "type": "nominal"
                },
                "tooltip": [
                    {
                        "field": "Category",
                        "type": "nominal"
                    },
                    {
                        "field": "Amount",
                        "type": "quantitative"
                    }
                ]
            }
        },
        use_container_width=True
    )

else:
    st.info(
        "No approved expenses available for the chart."
    )


# ==================================
# 10. CATEGORY BUDGET BREAKDOWN
# ==================================

st.divider()
st.write("**Budget Breakdown by Category**")

all_categories = sorted(
    set(budget_dict) | set(expense_dict)
)

category_rows = []

for category in all_categories:

    budget_limit = budget_dict.get(category, 0)
    spent = expense_dict.get(category, 0)
    remaining = budget_limit - spent

    if category not in budget_dict:
        status = "No Budget Allocated"

    elif remaining < 0:
        status = "Over Budget"

    else:
        status = "Within Budget"

    category_rows.append({
        "Category": category,
        "Budget (RM)": round(budget_limit, 2),
        "Approved Expenses (RM)": round(spent, 2),
        "Remaining (RM)": round(remaining, 2),
        "Status": status
    })


if category_rows:

    category_df = pd.DataFrame(category_rows)

    st.dataframe(
        category_df,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info(
        "No category budgets or approved expenses yet."
    )


# ==================================
# 11. FINANCIAL INSIGHTS
# ==================================

st.divider()
st.subheader("Financial Insights")


# Highest Spending Category

if category_expenses:

    highest_category = max(
        category_expenses,
        key=lambda item: item[1]
    )

    st.info(
        f"Highest spending category: {highest_category[0]} "
        f"(RM {highest_category[1]:.2f})"
    )


# Category with Lowest Remaining Budget

if category_rows:

    lowest_category = min(
        category_rows,
        key=lambda item: item["Remaining (RM)"]
    )

    st.info(
        f"Lowest remaining budget: {lowest_category['Category']} "
        f"(RM {lowest_category['Remaining (RM)']:.2f})"
    )


# Overall Spending Insights

if total_budget > 0 and total_expenses > total_budget:

    st.warning(
        "The club has exceeded its overall budget."
    )

elif total_budget > 0:

    st.success(
        "The club is currently within its overall budget."
    )


# Low Remaining Budget Alert

if total_budget > 0 and remaining_percentage <= 20:

    st.warning(
        "Warning! Only 20% or less of the club budget remains."
    )


# ==================================
# 12. OVERALL CLUB BUDGET STATUS
# ==================================

st.divider()
st.write("**Overall Club Budget Status**")

if total_budget == 0:

    st.info("No budget has been allocated yet.")

elif remaining_budget < 0:

    st.error("Over Budget")

elif remaining_percentage <= 20:

    st.warning("Budget Running Low")

else:

    st.success("Budget Healthy")


