from narwhals import nth
import streamlit as st

st.set_page_config(
    page_title="Club Budget Tracker",
    page_icon="💰",
    layout="wide"
)
st.markdown("""
    <style>
    .stApp {
        background-color: #F8F5FF!important;
    }

    h1 {
        color: #8156C5!important;
    }

    h2, h3 {
        color: #A05ACB!important;
    }
    /* First dashboard card */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stMetric"] {
    background-color: #E9E1FF;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
}

/* Second dashboard card */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stMetric"] {
    background-color: #FFE4EB;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
}

/* Third dashboard card */
div[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetric"] {
    background-color: #DDF5EE;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    transition: 0.3s ease;
}
.stButton > button {
    width: 100% !important;
    background-color: #8156C5 !important;
    color: white !important;
    border-radius: 12px;
    border: none;
    padding: 10px 25px;
    font-weight: bold;
    font-size: 20px !important;
    transition: all 0.3s ease;
}
.stButton > button p {
    font-size: 20px !important;
}

.stButton > button:hover {
    background-color: #946FD0 !important;
    color: white !important;
    transform: translateY(-3px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}
.stApp h1, .stApp h2, .stApp h3{
    margin-bottom: 20px;
}

.stApp [data-testid="stMarkdownContainer"] p {
    line-height: 1.6;
}
    </style>
    """, unsafe_allow_html=True)


st.title("Club Budget and Expense Tracker")

st.write("Welcome to our club financial management system!")
st.subheader("Financial Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Budget", "Not set")

with col2:
    st.metric("Total Expenses", "No expenses yet")

with col3:
    st.metric("Remaining Budget", "Not available")

st.subheader("Main Features")

st.write("1. Record income and expense")
st.write("2. Monitor event budgets")
st.write("3. View financial history")
st.write("4. Receive budget alerts")

if st.button("Next"):
    st.switch_page("pages/1_Expense_Entry.py")