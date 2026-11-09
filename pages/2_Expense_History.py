import streamlit as st
from database import get_expenses,delete_expense
import plotly.express as px
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
# Calculate total expenses
total_expenses = sum(
    expense[2] for expense in get_expenses()
)

# Display expense history
st.subheader("Expenses History")
expenses = [
    {
        "ID" : row[0],
        "Expense Name": row[1],
        "Amount(RM)": row[2],
        "Category": row[3]
    }
    for row in get_expenses()
]
if expenses:
    st.dataframe(
        expenses,
        use_container_width=True,
        hide_index=True
    )

    st.metric(
        "Total Expenses",
        f"RM {total_expenses:.2f}"
    )

    # Delete expense
    st.subheader("Delete Expense")

    for expense in expenses:
        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(expense["Expense Name"])

        with col2:
            if st.button("Delete", key=f"delete_{expense['ID']}"):
                delete_expense(expense["ID"])
                st.rerun()

    # Spending by category
    category_totals = {}

    for expense in expenses:
        category = expense["Category"]
        amount = expense["Amount(RM)"]

        if category not in category_totals:
            category_totals[category] = 0

        category_totals[category] += amount

    st.subheader("Spending by Category")
    

else:
    st.info("No expenses recorded yet.")
category_totals={}
for expense in expenses:
    category = expense["Category"]
    amount = float(expense["Amount(RM)"])

    if category not in category_totals:
        category_totals[category] = 0

    category_totals[category]+=amount
st.subheader("Spending by Category")
fig = px.pie(
    names=list(category_totals.keys()),
    values=list(category_totals.values()),
    title="Spending by Category",
    hole=0.4
)

st.plotly_chart(fig, use_container_width=True)

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