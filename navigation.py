
import streamlit as st
#logout button
def show_logout_button():

    if st.sidebar.button("🚪 Log Out", key="global_logout"):

        st.session_state.pop("logged_in", None)
        st.session_state.pop("username", None)
        st.session_state.pop("user_id", None)
        st.session_state.pop("selected_club_id", None)
        st.session_state.pop("selected_club_name", None)

        st.switch_page("pages/0_Account.py")
        st.stop()

#sidebar
def show_finance_sidebar():
    # Hide Streamlit's default navigation menu
    st.markdown("""
        <style>
        /* Hide Streamlit's automatic page navigation */
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavItems"],
        .stSidebarNav {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.sidebar.title("💰 Finance Tracker")
    if st.sidebar.button("🏠 Finance Selection", use_container_width=True):
        st.switch_page("pages/1_Finance_Selection.py")
    st.sidebar.divider()
    
    st.sidebar.subheader("🏢 Club Finance")

    if st.sidebar.button("Club Navigation", use_container_width=True):
        st.switch_page("pages/5_Club_Navigation.py")

    if st.sidebar.button("Club Dashboard", use_container_width=True):
        st.switch_page("app.py")

    if st.sidebar.button("Club Budget Setting", use_container_width=True):
        st.switch_page("pages/6_Club_Budget_Setting.py")

    if st.sidebar.button("Club Expense History", use_container_width=True):
        st.switch_page("pages/7_Club_Expense_History.py")

    if st.sidebar.button("Club Expense Submission", use_container_width=True):
        st.switch_page("pages/9_Club_Expense_Submission.py")

    if st.sidebar.button("Club Expense Approval", use_container_width=True):
        st.switch_page("pages/8_Club_Expense_Approval.py")

    st.sidebar.divider()
    st.sidebar.subheader("📋 Programme Management")

    if st.sidebar.button("💳 Programme Deposit", use_container_width=True):
        st.switch_page("pages/11_programme_deposit.py")
    st.sidebar.divider()
    st.sidebar.subheader("👤 Personal Finance")

    if st.sidebar.button("Personal Dashboard", use_container_width=True):
        st.switch_page("pages/10_Personal_Dashboard.py")

    if st.sidebar.button("Expense Entry", use_container_width=True):
        st.switch_page("pages/2_Expense_Entry.py")

    if st.sidebar.button("Expense History", use_container_width=True):
        st.switch_page("pages/3_Expense_History.py")

    if st.sidebar.button("Budget Setting", use_container_width=True):
        st.switch_page("pages/4_Budget_Setting.py")

    st.sidebar.divider()

    show_logout_button()
#design

def show_custom_style():

    st.markdown("""
        <style>

        /* Main background */
        .stApp {
            background-color: #F7F3FC;
        }

        /* Headings */
        h1, h2, h3 {
            color: #7651A8;
        }

        /* Content cards */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: white;
            border: 1px solid #EAE1F5;
            border-radius: 14px;
            padding: 12px;
        }

        /* Buttons */
        div.stButton > button {
            background-color: #7651A8;
            color: white;
            border-radius: 9px;
            border: none;
            min-height: 42px;
        }

        div.stButton > button:hover {
            background-color: #60418B;
            color: white;
        }

        /* Dataframes */
        div[data-testid="stDataFrame"] {
            border-radius: 12px;
        }

        </style>
    """, unsafe_allow_html=True)
