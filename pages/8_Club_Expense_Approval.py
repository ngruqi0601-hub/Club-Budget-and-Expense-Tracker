
import streamlit as st
import os
from storage import download_receipt
from database import (
    get_club_expenses,
    get_user_id,
    get_user_club_role,
    update_expense_status
)

from navigation import show_finance_sidebar,show_custom_style


# --------------------------------
# 1. Page Configuration
# --------------------------------

st.set_page_config(
    page_title="Club Expense Approval",
    page_icon="✅",
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

if role != "Treasurer":
    st.error("Only the Treasurer can approve or reject expenses.")
    st.stop()


# --------------------------------
# 4. Page Header
# --------------------------------

st.title(f"✅ {club_name} Expense Approval")

if st.button("⬅️ Back to Club Navigation"):
    st.switch_page("pages/5_Club_Navigation.py")

st.divider()


# --------------------------------
# 5. Retrieve Pending Expenses
# --------------------------------

expenses = get_club_expenses(club_id)

pending_expenses = [
    expense for expense in expenses
    if expense[6] == "Pending"
]


# --------------------------------
# 6. Display Pending Expenses
# --------------------------------

if pending_expenses:

    for expense in pending_expenses:

        expense_id = expense[0]
        expense_name = expense[1]
        amount = expense[2]
        category = expense[3]
        submitted_by = expense[4]
        receipt_path = expense[5]
        description = expense[8]

        if description and str(description).strip():
            st.write(f"**Description:** {description}")
        else:
            st.write("**Description:** No description")

        st.subheader(expense_name)

        st.write(f"**Amount:** RM {amount:.2f}")
        st.write(f"**Category:** {category}")
        st.write(f"**Submitted By:** {expense[4]}")

        # Member's Description
        if description and description.strip():
            st.write(f"**Description:** {description}")
        else:
            st.write("**Description:** No description provided.")

        # Display Receipt
        if receipt_path:
            try:
                receipt_data = download_receipt(receipt_path)

                if receipt_path.lower().endswith((".png", ".jpg", ".jpeg")):
                    st.image(
                        receipt_data,
                        caption="Uploaded Receipt",
                        width=250
                    )

                elif receipt_path.lower().endswith(".pdf"):
                    st.download_button(
                        label="Download Receipt",
                        data=receipt_data,
                        file_name=os.path.basename(receipt_path),
                        mime="application/pdf",
                        key=f"receipt_{expense_id}"
                    )

            except Exception as e:
                st.warning(f"Unable to retrieve receipt: {e}")

        else:
            st.warning("No receipt uploaded.")

        # Treasurer's Optional Remarks
        remarks = st.text_area(
            "Treasurer's Remarks (Optional)",
            placeholder="Explain your approval or rejection decision (if applicable)...",
            key=f"remarks_{expense_id}"
        )

        # Approve and Reject Buttons
        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "✅ Approve",
                key=f"approve_{expense_id}",
                use_container_width=True
            ):

                success = update_expense_status(
                    expense_id,
                    club_id,
                    user_id,
                    "Approved",
                    remarks.strip() or None
                )

                if success:
                    st.success("Expense approved successfully!")
                    st.rerun()

                else:
                    st.error("Unable to approve expense.")

        with col2:

            if st.button(
                "❌ Reject",
                key=f"reject_{expense_id}",
                use_container_width=True
            ):

                success = update_expense_status(
                    expense_id,
                    club_id,
                    user_id,
                    "Rejected",
                    remarks.strip() or None
                )

                if success:
                    st.warning("Expense rejected.")
                    st.rerun()

                else:
                    st.error("Unable to reject expense.")

        st.divider()


else:

    st.info("There are no pending expenses.")
