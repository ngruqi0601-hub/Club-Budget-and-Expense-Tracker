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

if st.button("Submit Expense"):
    st.write("Expense Name:", expense_name)
    st.write("Amount: RM", amount)
    st.write("Category:", category)     
if category == "Others":
    custom_category = st.text_input("Please specify your category")
else:
    custom_category = ""