import streamlit as st
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
if "budget" not in st.session_state:
    st.session_state.budget=0.0
budget=st.number_input(
    "Enter total budget(RM)",
    min_value=0.0,
    step=100.0
)
if st.button("Submit Budget",key="submit budget"):
    if budget<=0:
        st.warning("Please enter a value")
    else:
        st.session_state.budget=budget
        st.success("Budget submitted successfully!")
st.subheader("Current BUdget:RM"+str(st.session_state.budget))
if "expenses" not in st.session_state:
    st.session_state.expenses = []

total_expenses = sum(
    float(expense["Amount(RM)"])
    for expense in st.session_state.expenses
)
remaining_budget=st.session_state.budget-total_expenses
st.metric("Total Budget" , f"RM{st.session_state.budget:.2f}")
st.metric("Total Expenses", f"RM{total_expenses:.2f}")
st.metric("Remaining Budget", f"RM{remaining_budget:.2f}")
if remaining_budget < 0:
    st.error("You have exceeded your budget!")

elif remaining_budget == 0:
    st.warning("You have used your entire budget!")

else:
    st.success("You are within your budget!")
if st.session_state.budget > 0:
    spending_ratio = total_expenses / st.session_state.budget

    st.subheader("Budget Usage")
    st.progress(min(spending_ratio, 1.0))

    st.write(f"Budget Used: {spending_ratio * 100:.1f}%")