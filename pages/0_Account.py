import streamlit as st
from database import register_user, login_user

st.title("Welcome to the Club Budget and Expense Tracker")
st.subheader("Please log in or create an account to continue.")

register_tab, login_tab = st.tabs(["Create Account", "Log In"])
with register_tab:
    st.subheader("Create a New Account")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Create Account"):
       if not username or not email or not password or not confirm_password:
        st.warning("Please fill in all fields.")

       elif password != confirm_password:
        st.warning("Passwords do not match.")
       else:
        success = register_user(username, email, password)

        if success:
            st.success("Account created successfully!")
        else:
            st.error("Username or email already exists.")
with login_tab:
    st.subheader("Welcome Back")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )

    if st.button("Log In"):
      if not login_username or not login_password:
        st.warning("Please enter your username and password.")

      else:
        success = login_user(login_username, login_password)

        if success:
            st.session_state.logged_in=True
            st.session_state.username = login_username
            st.success("Login successful!")
            st.switch_page("app.py")
        else:
            st.error("Invalid username or password.")