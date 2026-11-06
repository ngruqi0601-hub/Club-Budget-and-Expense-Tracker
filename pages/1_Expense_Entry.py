import streamlit as st

st.title("Add New Expense")

if "expenses" not in st.session_state:
    st.session_state.expenses = []

expense_name = st.text_input("Expense Name")

amount = st.number_input(
    "Amount (RM)",
    min_value=0.0,
    step=1.0
)

category = st.selectbox(
    "Category",
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

if category == "Others":
    custom_category = st.text_input("Please specify your category")
else:
    custom_category = ""

if category == "Others":
    final_category = custom_category
else:
    final_category = category

if st.button("Submit Expense", key="submit_expense"):

    if expense_name.strip() == "":
        st.warning("Please enter an expense name.")

    elif amount <= 0:
        st.warning("Please enter an amount greater than RM0.")

    elif category == "Others" and custom_category.strip() == "":
        st.warning("Please specify your category.")

    else:
        st.session_state.expenses.append({
            "Expense Name": expense_name,
            "Amount(RM)": amount,
            "Category": final_category
        })

        st.success("Expense submitted successfully!")

if st.button("Next"):
    st.switch_page("pages/2_Expense_History.py")