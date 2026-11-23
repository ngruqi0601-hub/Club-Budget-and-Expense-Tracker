
import streamlit as st
import pandas as pd
import os
from storage import download_receipt
from database import (
    get_club_expenses,
    get_user_id,
    get_user_club_role,
    get_username
)
from navigation import show_finance_sidebar,show_custom_style


# Page configuration
st.set_page_config(
    page_title="Club Expense History",
    page_icon="📋",
    layout="wide"
)

show_finance_sidebar()
#design
show_custom_style()


# Check login
if not st.session_state.get("logged_in", False) or not st.session_state.get("username"):
    st.warning("Please log in first.")
    st.switch_page("pages/0_Account.py")
    st.stop()


# Check selected club
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


# Page title
st.title(f"📋 {club_name} Expense History")
st.write("View all expenses submitted to this club.")

if st.button("⬅️ Back to Club Navigation"):
    st.switch_page("pages/5_Club_Navigation.py")

st.divider()


# Retrieve club expenses
expenses = get_club_expenses(club_id)

if expenses:
    expense_data = []

    for expense in expenses:
        expense_data.append({
            "Expense Name": expense[1],
            "Amount (RM)": expense[2],
            "Category": expense[3],
            "Submitted By": get_username(expense[4]),
            "Status": expense[6],
            "Date": expense[7],
            "Description": expense[8] or "No description provided",
            "Treasurer's Remarks": expense[9] or "No remarks provided"
        })

    df = pd.DataFrame(expense_data)

    st.subheader("All Club Expenses")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # View receipt downloads
    st.subheader("🧾 View Expense Receipts")

    for expense in expenses:
        expense_id = expense[0]
        expense_name = expense[1]
        receipt_path = expense[5]

        with st.expander(f"📄 {expense_name}"):

            if receipt_path:
                receipt_data = download_receipt(receipt_path)

                if receipt_data:
                    st.download_button(
                        label="Download Receipt",
                        data=receipt_data,
                        file_name=os.path.basename(receipt_path),
                        key=f"receipt_{expense_id}"
                    )
                else:
                    st.warning("Receipt file not found in Supabase Storage.")
            else:
                st.warning("No receipt attached to this expense.")

    else:
        st.info("No club expenses have been submitted yet.")