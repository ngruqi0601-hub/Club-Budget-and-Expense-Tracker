import streamlit as st
import os
import uuid
from database import (
    add_club_expense,
    get_user_id,
    get_user_club_role
)
if not st.session_state.get("logged_in", False) or not st.session_state.get("username"):
    st.warning("Please log in first.")
    st.switch_page("pages/0_Account.py")
    st.stop()

if "selected_club_id" not in st.session_state:
    st.warning("Please select a club from the dashboard.")
    st.stop()

club_id = st.session_state.selected_club_id
user_id = get_user_id(st.session_state.username)

role = get_user_club_role(user_id, club_id)

if role is None:
    st.error("You are not a member of this club.")
    st.stop()
os.makedirs("receipts",exist_ok=True)
st.title("Club Expense Submission")

st.subheader("Submit a New Expense")

expense_name = st.text_input("Expense Name")

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
    type=["png", "jpg", "jpeg", "pdf"]
)
if st.button("Submit Expense"):

    if not expense_name.strip():
        st.warning("Please enter an expense name.")

    elif receipt is None:
        st.warning("Please upload a receipt.")

    else:
        file_extension = os.path.splitext(receipt.name)[1]
        file_name = f"{uuid.uuid4().hex}{file_extension}"
        receipt_path = os.path.join("receipts", file_name)

        with open(receipt_path, "wb") as file:
            file.write(receipt.getbuffer())

        add_club_expense(
            club_id,
            user_id,
            expense_name,
            amount,
            category,
            receipt_path
        )

        st.success("Expense submitted successfully!")
        st.info("Your expense is now pending Treasurer approval.")
