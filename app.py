import streamlit as st
st.set_page_config(
    page_title="Club Budget Tracker",
    page_icon="💰"
)
st.title("Club Budget and Expense Tracker")
st.write("Welcome to our club financial management system!")
st.subheader("Main Features")
st.write("1.Record income and expense")
st.write("2.Monitor event budgets")
st.write("3. View financial history")
st.write("4.Receive budget alert")
st.subheader("Add New Expense")

expense_name = st.text_input("Expense Name")

amount = st.number_input(
    "Amount (RM)",
    min_value=0.0,
    step=1.0
)

category = st.selectbox(
    "Category",
    ["Food", "Transportation", "Equipment", "Acommodation","Workshop Materials","Utilities","Competition Fees","Menbership Activities","Others"]
)
if category == "Others":
    custom_category = st.text_input("Please specify your category")
else:
    custom_category = ""
if category=="Others":
   final_category=custom_category
else:
    final_category=category
if "expenses" not in st.session_state:
    st.session_state.expenses=[]
if st.button("Submit Expense", key="submit_expense"):

    if expense_name == "":
        st.warning("Please enter an expense name.")

    elif amount <= 0:
        st.warning("Please enter an amount greater than RM0.")

    elif category == "Others" and custom_category.strip() == "":
        st.warning("Please specify your category.")

    else:
        st.success("Expense submitted successfully!")

        st.write("Expense Name:", expense_name)
        st.write("Amount: RM", amount)
        st.write("Category:", final_category)
    
        st.session_state.expenses.append({
            "Expense Name": expense_name,
            "Amount(RM)": amount,
            "Category": final_category
        })
total_expenses = sum(
    expense["Amount(RM)"]
    for expense in st.session_state.expenses
)
expense_summary = st.session_state.expenses.copy()

expense_summary.append({
    "Expense Name": "TOTAL EXPENSES",
    "Amount(RM)": total_expenses,
    "Category": ""
})
st.subheader("Expenses History")
st.table(expense_summary)
