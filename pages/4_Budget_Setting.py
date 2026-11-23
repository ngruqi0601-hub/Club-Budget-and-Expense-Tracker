import streamlit as st
from database import add_budget, get_budgets,get_expenses,update_budget,delete_budget
from navigation import show_finance_sidebar
if not st.session_state.get("logged_in", False):
    st.warning("Please log in to access this page.")
    st.switch_page("pages/0_Account.py")
show_finance_sidebar()
#page design
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
user_id=st.session_state.user_id
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
budgets = get_budgets(user_id)
if st.button("Submit Budget", key="submit_budget"):
    if budget_limit <= 0:
        st.warning("Please enter a valid budget limit.")

    elif any(row[2].strip().lower() == category.strip().lower() for row in budgets):
        st.warning("A budget already exists for this category.")

    else:
        success = add_budget(user_id, category, budget_limit)

        if success:
            st.session_state.budget_added = category
            st.rerun()
        else:
            st.error("Unable to add budget. Please check the details or try again.")
if st.session_state.get("budget_added"):
    st.success(
        f"Budget for {st.session_state.budget_added} submitted successfully!"
    )
    del st.session_state.budget_added
st.subheader("Update Existing Budget")


if budgets:
    existing_categories = [row[2] for row in budgets]

    selected_category = st.selectbox(
        "Select Category to Update",
        existing_categories
    )
    current_budget = 0.0

    for row in budgets:
        if row[2] == selected_category:
            try:
                current_budget = float(row[3])
            except (ValueError, TypeError):
                current_budget = 0.0
            break
    st.write(f"Current Budget: RM {current_budget:.2f}")
    new_budget_limit = st.number_input(
        "Enter New Budget Limit (RM)",
        min_value=0.01,
        value=max(float(current_budget), 0.01),
        step=10.0,
        key=f"update_{selected_category}"
    )
    if st.button("Update Budget", key="update_budget"):
       if new_budget_limit == current_budget:
          st.warning("No changes detected.")
       else:
          update_budget(user_id,selected_category, new_budget_limit)
          st.success(f"{selected_category} budget updated successfully!")
          st.rerun()
else:
    st.info("No budgets available to update.")
st.divider()
st.subheader("Delete Existing Budget")

budgets = get_budgets(user_id)

if budgets:
    delete_category = st.selectbox(
        "Select Category to Delete",
        [row[2] for row in budgets],
        key="delete_category"
    )

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this budget."
    )

    if st.button("Delete Budget", key="delete_budget"):
        if confirm_delete:
            success = delete_budget(user_id, delete_category)

            if success:
                st.success(f"{delete_category} budget deleted successfully!")
                st.rerun()
            else:
                st.error("Unable to delete budget. Please try again.")
        else:
            st.warning("Please confirm before deleting.")
else:
    st.info("No budgets available to delete.")
st.subheader("Budget Overview")

budgets = get_budgets(user_id)
expenses = get_expenses(user_id)
category_totals = {}

for expense in expenses:
    category_name = expense[3]
    amount = float(expense[2])

    if category_name not in category_totals:
        category_totals[category_name] = 0

    category_totals[category_name] += amount
if budgets:
    for budget in budgets:
        budget_id = budget[0]
        category_name = budget[2]
        try:
            budget_limit = float(budget[3])
        except (ValueError, TypeError):
            st.warning(f"Invalid budget value for {category_name}. Please update this budget.")
            continue
        actual_spending = category_totals.get(category_name, 0)
        remaining = budget_limit - actual_spending
        spending_ratio = actual_spending / budget_limit if budget_limit > 0 else 0
        st.markdown(f"###{category_name}")
        col1, col2, col3 = st.columns(3)

        col1.metric("Budget", f"RM {budget_limit:.2f}")
        col2.metric("Spent", f"RM {actual_spending:.2f}")
        col3.metric("Remaining", f"RM {remaining:.2f}")
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
col1, col2 = st.columns(2)

with col1:
    if st.button("Back"):
        st.switch_page("pages/3_Expense_History.py")

with col2:
    if st.button("Next"):
        st.switch_page("pages/10_Personal_Dashboard.py")