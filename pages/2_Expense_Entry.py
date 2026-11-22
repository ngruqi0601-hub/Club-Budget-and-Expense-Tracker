import streamlit as st
from database import add_expense
from navigation import show_finance_sidebar
if not st.session_state.get("logged_in", False):
    st.warning("Please log in to access this page.")
    st.switch_page("pages/0_Account.py")
show_finance_sidebar()
#page design
st.markdown("""
    <style>
    .stApp {
    background-color: #F8F5FF !important;
}
.stApp h1,
.stApp h2,
.stApp h3 {
    color: #8156C5 !important;
    font-weight: bold;
}
.stApp h1 {
    letter-spacing: 1px;
    margin-bottom: 15px;
}
    .stTextInput input,
    .stNumberInput input {
    background-color: #F3EDFF !important;
}
   div[data-testid="stSelectbox"] [data-baseweb="select"],
div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
div[data-testid="stSelectbox"] [data-baseweb="select"] > div > div {
    background-color: #F3EDFF !important;
    border-radius: 10px !important;
}
    .stTextInput,
    .stNumberInput,
    .stSelectbox {
        margin-bottom: 15px;
}
.stTextInput input:focus,
.stNumberInput input:focus {
    border: 2px solid #8156C5 !important;
    box-shadow: 0 0 5px rgba(129, 86, 197, 0.3);
}
.stTextInput input:hover,
.stNumberInput input:hover {
    border: 1px solid #A080D5 !important;
}
.stTextInput label,
.stNumberInput label,
.stSelectbox label {
    color: #60418F !important;
    font-weight: bold !important;
}
.stTextInput input,
.stNumberInput input {
    color: #60418F !important;
    font-weight: 500;
}
.stTextInput input::placeholder,
.stNumberInput input::placeholder {
    color: #B09ACF !important;
    opacity: 1;
}
.stTextInput input,
.stNumberInput input {
    border-radius: 12px !important;
}
.stButton > button {
    width:100% !important;
    padding: 12px;
    background-color: #8156C5 !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    font-weight: bold;
    transition: 0.3s ease;
}

.stButton > button:hover {
    background-color: #A080D5 !important;
    transform: translateY(-3px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}
.stButton > button {
    box-shadow: 0 4px 8px rgba(129, 86, 197, 0.25);
}
/* Back button */
div[data-testid="stHorizontalBlock"] div:nth-child(1) .stButton > button {
    background-color: #E9E1FF !important;
    color: #8156C5 !important;
}

/* Next button */
div[data-testid="stHorizontalBlock"] div:nth-child(2) .stButton > button {
    background-color: #8156C5 !important;
    color: white !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
    border-radius: 15px !important;
    border: 1px solid #E5D9F5 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 6px 16px rgba(129, 86, 197, 0.18);
    transition: 0.3s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    padding: 10px !important;
}
.stButton > button:active {
    transform: scale(0.97);
    box-shadow: none;
}
.stNumberInput button {
    color: #8156C5 !important;
    border-radius: 8px !important;
}
.stSelectbox svg {
    fill: #8156C5 !important;
    color: #8156C5 !important;
}
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    padding: 12px !important;
}
.stApp hr {
    border-color: #D8C5F2 !important;
    margin: 20px 0;
}
    </style>
""", unsafe_allow_html=True)

st.title("Add New Expense💰")
st.write("Please fill in the details of your expense below:")
st.divider()

if "expenses" not in st.session_state:
    st.session_state.expenses = []
with st.container(border=True):
    st.subheader("Expense Details")
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
    ],
      key="category",
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
        user_id = st.session_state.user_id
        add_expense(user_id, expense_name, amount, final_category)
        st.success("Expense submitted successfully!")
col1, col2 = st.columns(2)

with col1:
    if st.button("Back"):
        st.switch_page("pages/10_Personal_Dashboard.py")

with col2:
    if st.button("Next"):
        st.switch_page("pages/3_Expense_History.py")