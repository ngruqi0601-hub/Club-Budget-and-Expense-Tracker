
import streamlit as st
from database import get_expenses, get_budgets,migrate_personal_data
from navigation import show_finance_sidebar,show_custom_style

st.set_page_config(
    page_title="Personal Dashboard",
    page_icon="💜",
    layout="wide"
)
show_finance_sidebar()
#design
show_custom_style()
# Check login
if not st.session_state.get("logged_in", False):
    st.warning("Please log in to access this page.")
    st.switch_page("pages/0_Account.py")
user_id=st.session_state.user_id
migrate_personal_data(user_id)

expenses = get_expenses(user_id)
budgets = get_budgets(user_id)


# Page styling
st.markdown("""
<style>
.stApp {
    background-color: #F8F5FF !important;
}
.stApp h1,
.stApp h2,
.stApp h3 {
    color: #8156C5 !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Navigation
if st.button("🏠 Finance Selection", key="personal_finance_selection"):
    st.switch_page("pages/1_Finance_Selection.py")

st.title("Personal Finance Dashboard 💜")
st.write("Welcome to your personal financial management page.")

st.divider()

# Navigation cards
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.subheader("💰 Expense Entry")
        st.write("Record your personal expenses.")
        if st.button("Add Expense", key="personal_add_expense"):
            st.switch_page("pages/2_Expense_Entry.py")

with col2:
    with st.container(border=True):
        st.subheader("📊 Expense History")
        st.write("Review your spending history.")
        if st.button("View History", key="personal_view_history"):
            st.switch_page("pages/3_Expense_History.py")


with col3:
    with st.container(border=True):
        st.subheader("🎯 Budget Setting")
        st.write("Set and monitor your budgets.")
        if st.button("Manage Budget", key="personal_manage_budget"):
            st.switch_page("pages/4_Budget_Setting.py")
total_expenses = sum(row[2] for row in expenses)
total_budget = sum(row[3] for row in budgets)
remaining_budget = total_budget - total_expenses

st.subheader("💰 Personal Financial Summary")

summary = {
    "Financial Summary": [
        "Total Budget",
        "Total Expenses",
        "Remaining Budget"
    ],
    "Amount (RM)": [
        f"{total_budget:.2f}",
        f"{total_expenses:.2f}",
        f"{remaining_budget:.2f}"
    ]
}

st.table(summary)