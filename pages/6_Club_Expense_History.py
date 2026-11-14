import streamlit as st
import pandas as pd
import os

from database import (
    get_club_expenses,
    get_user_id,
    get_user_club_role,
    get_username
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
st.title("Club Expense History")

expenses = get_club_expenses(club_id)

if expenses:
    expense_data = []

    for expense in expenses:
        expense_data.append({
            "Expense Name": expense[1],
            "Amount (RM)": expense[2],
            "Category": expense[3],
            "Submitted By": get_username(expense[4]),
            "Receipt": expense[5],
            "Status": expense[6],
            "Date": expense[7]
        })

    df = pd.DataFrame(expense_data)

    st.dataframe(df, use_container_width=True)
    st.divider()
    st.subheader("View Expense Receipts")

    for expense in expenses:
       expense_name = expense[1]
       receipt_path = expense[5]

       if os.path.exists(receipt_path):
            with open(receipt_path, "rb") as file:
                st.download_button(
                   label=f"Download Receipt - {expense_name}",
                   data=file,
                   file_name=os.path.basename(receipt_path),
                   key=f"receipt_{expense[0]}"
            )
       else:
             st.warning(f"Receipt not found for {expense_name}.")

else:
    st.info("No club expenses have been submitted yet.")