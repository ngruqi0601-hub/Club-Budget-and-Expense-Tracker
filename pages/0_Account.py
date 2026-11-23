import streamlit as st
from database import register_user, login_user, check_account_exists, get_user_id,send_verification_email,reset_password
import secrets
import time

st.title("Welcome to the Club Budget and Expense Tracker")
st.subheader("Please log in or create an account to continue.")

register_tab, login_tab = st.tabs(["Create Account", "Log In"])
with register_tab:
    st.subheader("Create a New Account")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input(
    "Password",
    type="password"
)

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

    # Normal Login Section
    if not st.session_state.get("forgot_password", False):

        login_username = st.text_input(
            "Username",
            key="login_username"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Forgot Password?"):
            st.session_state.forgot_password = True
            st.rerun()

        if st.button("Log In"):

            if not login_username or not login_password:
                st.warning("Please enter your username and password.")

            else:
                success = login_user(login_username, login_password)

                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = login_username

                    user_id = get_user_id(login_username)
                    st.session_state.user_id = user_id

                    st.success("Login successful!")
                    st.switch_page("pages/1_Finance_Selection.py")

                else:
                    st.error("Invalid username or password.")

    # Forgot Password Section
    else:

        st.subheader("Reset Password")

        username = st.text_input("Enter your username")
        email = st.text_input("Enter your registered email")

        if st.button("Continue"):

            if not username.strip() or not email.strip():
                st.warning("Please enter both username and email.")

            elif check_account_exists(username.strip(), email.strip()):

                verification_code = str(
                    secrets.randbelow(900000) + 100000
                )

                try:
                    send_verification_email(
                        email.strip(),
                        verification_code
                    )

                    st.session_state.verification_code = verification_code
                    st.session_state.verification_email = email.strip()
                    st.session_state.verification_username = username.strip()
                    st.session_state.code_expiry = time.time() + 300
                    st.session_state.code_verified = False

                    st.success("Verification code sent to your email!")

                except Exception as e:
                    st.error(f"Unable to send email: {e}")

            else:
                st.error("Username and email do not match any registered account.")

        # Verify Code Section
        if "verification_code" in st.session_state:

            st.subheader("Verify Your Email")

            entered_code = st.text_input(
                "Enter your 6-digit verification code",
                max_chars=6
            )

            if st.button("Verify Code"):

                if time.time() > st.session_state.code_expiry:
                    st.session_state.code_verified = False
                    st.error("Verification code has expired. Please request a new one.")

                elif entered_code == st.session_state.verification_code:
                    st.session_state.code_verified = True
                    st.success("Email verified successfully!")

                else:
                    st.error("Incorrect verification code.")

        # New Password Section
        if st.session_state.get("code_verified", False):

            st.subheader("Create New Password")

            new_password = st.text_input(
                "New Password",
                type="password",
                key="new_password"
            )

            confirm_new_password = st.text_input(
                "Confirm New Password",
                type="password",
                key="confirm_new_password"
            )

            if st.button("Reset Password"):

                if time.time() > st.session_state.code_expiry:
                    st.session_state.code_verified = False
                    st.error("Verification code has expired. Please request a new one.")

                elif not new_password or not confirm_new_password:
                    st.warning("Please fill in both password fields.")

                elif len(new_password) < 8:
                    st.warning("Password must contain at least 8 characters.")

                elif new_password != confirm_new_password:
                    st.error("Passwords do not match.")

                else:
                    success = reset_password(
                        st.session_state.verification_username,
                        st.session_state.verification_email,
                        new_password
                    )

                    if success:
                        st.success("Password reset successfully!")

                        st.session_state.pop("verification_code", None)
                        st.session_state.pop("verification_email", None)
                        st.session_state.pop("code_expiry", None)
                        st.session_state.pop("code_verified", None)

                        st.session_state.forgot_password = False

                    else:
                        st.error("Unable to reset password.")

        # Back to Login
        if st.button("Back to Login"):

            st.session_state.forgot_password = False

            st.session_state.pop("verification_code", None)
            st.session_state.pop("verification_username", None)
            st.session_state.pop("verification_email", None)
            st.session_state.pop("code_expiry", None)
            st.session_state.pop("code_verified", None)

            st.rerun()

        
    