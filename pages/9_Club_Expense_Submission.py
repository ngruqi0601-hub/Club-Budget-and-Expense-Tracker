
import streamlit as st
import os
import uuid
from storage import upload_receipt
from database import (
    add_club_expense,
    get_user_id,
    get_user_club_role
)

from navigation import show_finance_sidebar,show_custom_style


# --------------------------------
# 1. Page Configuration
# --------------------------------

st.set_page_config(
    page_title="Club Expense Submission",
    page_icon="📝",
    layout="wide"
)

show_finance_sidebar()
#design
show_custom_style()

# --------------------------------
# 2. Login Check
# --------------------------------

if not st.session_state.get("logged_in", False) or not st.session_state.get("username"):
    st.warning("Please log in first.")
    st.switch_page("pages/0_Account.py")
    st.stop()


# --------------------------------
# 3. Selected Club Check
# --------------------------------

club_id = st.session_state.get("selected_club_id")

if club_id is None:
    st.warning("Please select a club first.")

    if st.button("Select Club"):
        st.switch_page("pages/5_Club_Navigation.py")

    st.stop()


club_name = st.session_state.get("selected_club_name", "Selected Club")

user_id = get_user_id(st.session_state.username)

role = get_user_club_role(user_id, club_id)

if role is None:
    st.error("You are not a member of this club.")
    st.stop()


# --------------------------------
# 4. Page Header
# --------------------------------

st.title(f"📝 {club_name} Expense Submission")

if st.button("⬅️ Back to Club Navigation"):
    st.switch_page("pages/5_Club_Navigation.py")

st.divider()


# --------------------------------
# 5. Create Receipt Folder
# --------------------------------

os.makedirs("receipts", exist_ok=True)


# --------------------------------
# 6. Expense Submission Form
# --------------------------------

st.subheader("Submit a New Expense")
expense_name = st.text_input(
    "Expense Name",
    key="club_expense_name"
)
description = st.text_area(
    "Expense Description",
    placeholder="Explain the purpose of this expense and provide additional details..."
)

amount = st.number_input(
    "Amount (RM)",
    min_value=0.01,
    step=1.00
)

category = st.selectbox(
    "Expense Category",
    [
        "Food",
        "Transportation",
        "Equipment",
        "Accommodation",
        "Workshop Materials",
        "Utilities",
        "Competition Fees",
        "Membership Activities",
        "Certificate and Awards",
        "Registration and Administration",
        "Prizes and Gifts",
        "Others"
    ]
)

receipt = st.file_uploader(
    "Upload Receipt",
    type=["png", "jpg", "jpeg", "pdf"],
    key="club_expense_receipt"
)


# --------------------------------
# 7. Submit Expense
# --------------------------------

if st.button("Submit Expense"):

    if not expense_name.strip():
        st.warning("Please enter an expense name.")

    elif receipt is None:
        st.warning("Please upload a receipt.")

    else:

        try:
            receipt_path = upload_receipt(receipt, club_id)

            add_club_expense(
                club_id,
                user_id,
                expense_name,
                amount,
                category,
                receipt_path
            )

            st.success("Expense submitted successfully!")
            st.info("Your expense is pending Treasurer approval.")

            

        except Exception as e:
            st.error(f"Unable to submit expense: {e}")