import streamlit as st
import os

from database import (
    get_club_expenses,
    get_user_id,
    get_user_club_role,
    update_expense_status
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

if role != "Treasurer":
    st.error("Only the Treasurer can approve or reject expenses.")
    st.stop()
expenses = get_club_expenses(club_id)

pending_expenses = [
    expense for expense in expenses
    if expense[6] == "Pending"
]

if pending_expenses:
    for expense in pending_expenses:

        expense_id = expense[0]
        expense_name = expense[1]
        amount = expense[2]
        category = expense[3]
        submitted_by = expense[4]
        receipt_path = expense[5]

        st.subheader(expense_name)

        st.write(f"Amount: RM {amount:.2f}")
        st.write(f"Category: {category}")
        st.write(f"Submitted By: {submitted_by}")
        if os.path.exists(receipt_path):
            if receipt_path.lower().endswith((".png", ".jpg", ".jpeg")):
               st.image(receipt_path, caption="Uploaded Receipt")

            elif receipt_path.lower().endswith(".pdf"):
               with open(receipt_path, "rb") as file:
                  st.download_button(
                     label="Download Receipt",
                     data=file,
                     file_name=os.path.basename(receipt_path),
                     key=f"receipt_{expense_id}"
            )
        else:
            st.warning("Receipt file not found.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Approve", key=f"approve_{expense_id}"):
                success = update_expense_status(
                expense_id, club_id, user_id, "Approved"
        )

                if success:
                   st.success("Expense approved!")
                else:
                   st.error("Unable to approve expense.")
                st.rerun()

        with col2:
            if st.button("Reject", key=f"reject_{expense_id}"):
                success = update_expense_status(
                expense_id, club_id, user_id, "Rejected"
        )

                if success:
                   st.warning("Expense rejected!")
                else:
                   st.error("Unable to reject expense.")
                st.rerun()
            st.divider()

else:
    st.info("There are no pending expenses.")
