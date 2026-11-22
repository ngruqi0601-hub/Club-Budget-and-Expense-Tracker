import streamlit as st
from navigation import show_finance_sidebar, show_custom_style
st.set_page_config(
    page_title="Finance Selection",
    page_icon="💰",
    layout="wide"
)
#sidebar
show_finance_sidebar()
#design
show_custom_style()

if not st.session_state.get("logged_in", False):
    st.warning("Please log in first.")
    st.switch_page("pages/0_Account.py")

st.title("Welcome to Finance Management 💰")
st.write("What would you like to manage today?")

st.divider()

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("🏢 Club Finance")
        st.write(
            "Manage club budgets, expenses, "
            "submissions and approvals."
        )

        if st.button("Manage Club Finance"):
            st.switch_page("pages/5_Club_Navigation.py")

with col2:
    with st.container(border=True):
        st.subheader("👤 Personal Finance")
        st.write(
            "Manage your personal expenses, "
            "budgets and spending history."
        )

        if st.button("Manage Personal Finance"):
            st.switch_page("pages/10_Personal_Dashboard.py")