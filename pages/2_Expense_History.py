import streamlit as st
st.markdown("""
<style>

/* Page background */
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

/* Metric cards */
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

/* Buttons */
.stButton > button {
    background-color: #A080D5 !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
}

/* Force the button text to be white */
.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: white !important;
}

.stButton > button:hover {
    background-color: #8156C5 !important;
}


/* Divider */
.stApp hr {
    border-color: #D8C5F2 !important;
}

/* Table */
div[data-testid="stDataFrame"] {
    border: 1px solid #E5D9F5;
    border-radius: 12px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)


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
category_totals={}
for expense in st.session_state.expenses:
    category = expense["Category"]
    amount = float(expense["Amount(RM)"])

    if category not in category_totals:
        category_totals[category] = 0

    category_totals[category]+=amount
st.subheader("Spending by Category")

if category_totals:
    st.bar_chart(
        category_totals,
        horizontal=True
    )
else:
    st.info("No expense data available.")
col1,col2=st.columns(2)
with col1:
    if st.button("Back"):
       st.switch_page("pages/1_Expense_Entry.py")
with col2:
    if st.button("Next"):
       st.switch_page("pages/3_Budget_Setting.py")
category_totals = {}