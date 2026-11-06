import streamlit as st
st.title("Expense History")
if "expenses" not in st.session_state:
    st.session_state.expenses = []

total_expenses = sum(
    float(expense["Amount(RM)"])
    for expense in st.session_state.expenses
)

expense_summary = st.session_state.expenses.copy()
for expense in expense_summary:
    expense["Amount(RM)"]=f"{float(expense['Amount(RM)']):.2f}"

expense_summary.append({
    "Expense Name": "TOTAL EXPENSES",
    "Amount(RM)": f"{total_expenses:.2f}",
    "Category": ""
})

st.subheader("Expenses History")

st.table(expense_summary)
st.subheader("Delete Expense")
if st.session_state.expenses:
    cols=st.columns(len(st.session_state.expenses))
    for i, expense in enumerate(st.session_state.expenses):
        with cols[i]:
            if st.button(
               f"Delete {expense['Expense Name']}",
               key=f"delete_{i}"
            ):
               st.session_state.expenses.pop(i)
               st.rerun()
else:
    st.write("No expenses to delete.")
if st.button("Clear ALL Expenses",key="clear all"):
    st.session_state.expenses.clear()
    st.success("All Expenses Cleared Successfully")
    st.rerun()
col1,col2=st.columns(2)
with col1:
    if st.button("Back"):
       st.switch_page("pages/1_Expense_Entry.py")
with col2:
    if st.button("Next"):
       st.switch_page("pages/3_Budget_Setting.py")