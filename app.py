from narwhals import nth
import streamlit as st
from database import create_club,get_user_id,join_club,get_user_clubs
if not st.session_state.get("logged_in",False):
    st.warning("Please log in to access this page.")
    st.switch_page("pages/0_Account.py")
if st.button("Log Out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.switch_page("pages/0_Account.py")

st.set_page_config(
    page_title="Club Budget Tracker",
    page_icon="💰",
    layout="wide"
)
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
    display: none;
}
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
st.subheader("Create a Club")

club_name = st.text_input("Enter Club Name")

if st.button("Create Club"):
    if not club_name.strip():
        st.warning("Please enter a club name.")
    else:
        user_id = get_user_id(st.session_state.username)

        invitation_code = create_club(club_name, user_id)

        st.success("Club created successfully!")
        st.write("Your invitation code:")
        st.code(invitation_code)

st.subheader("Join a Club")

invitation_code = st.text_input("Enter Invitation Code")

if st.button("Join Club"):
    if not invitation_code.strip():
        st.warning("Please enter an invitation code.")

    else:
        user_id = get_user_id(st.session_state.username)

        result = join_club(invitation_code, user_id)

        if result == "success":
            st.success("You have successfully joined the club!")

        elif result == "invalid":
            st.error("Invalid invitation code.")

        elif result == "already_joined":
            st.warning("You have already joined this club.")

st.subheader("My Clubs")

user_id = get_user_id(st.session_state.username)

clubs = get_user_clubs(user_id)

if clubs:
    for club in clubs:
        club_id = club[0]
        club_name = club[1]
        role = club[2]

        st.write(f"**{club_name}**")
        st.write(f"Role: {role}")
        st.divider()
else:
    st.info("You haven't joined any clubs yet.")

if clubs:
    club_options = {
        club[1]: club[0]
        for club in clubs
    }

    selected_club = st.selectbox(
        "Select a Club",
        options=list(club_options.keys())
    )

    selected_club_id = club_options[selected_club]

    st.session_state.selected_club_id = selected_club_id

    st.success(f"Currently managing: {selected_club}")

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