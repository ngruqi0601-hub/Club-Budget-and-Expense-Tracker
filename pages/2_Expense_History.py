import streamlit as st
st.title("Expense History")
if "expenses" not in st.session_state:
    st.session_state.expenses = []

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
st.subheader("Delete Expense")

for i, expense in enumerate(st.session_state.expenses):
    if st.button(
        f"Delete {expense['Expense Name']}",
        key=f"delete_{i}"
    ):
        st.session_state.expenses.pop(i)
        st.rerun()