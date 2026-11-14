
import streamlit as st
from database import (
    add_club_budget,
    get_club_budgets,
    update_club_budget,
    delete_club_budget,
    get_user_club_role,
    get_user_id
)

# Check login
if not st.session_state.get("logged_in", False) or not st.session_state.get("username"):
    st.warning("Please log in to access this page.")
    st.switch_page("pages/0_Account.py")
    st.stop()

# Check selected club
if "selected_club_id" not in st.session_state:
    st.warning("Please select a club from the dashboard.")
    st.stop()

# Get club ID
club_id = st.session_state.selected_club_id

# Get user ID
user_id = get_user_id(st.session_state.username)

# Check membership
role = get_user_club_role(user_id, club_id)

if role is None:
    st.error("You are not a member of this club.")
    st.stop()

st.title("Club Budget Setting")
if role == "Treasurer":

    st.subheader("Add New Budget")

    category = st.selectbox(
        "Select Category",
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

    budget_limit = st.number_input(
        "Budget Limit (RM)",
        min_value=0.01,
        step=10.00
    )

    if st.button("Add Budget"):
        success = add_club_budget(
            club_id,
            category,
            budget_limit
        )

        if success:
            st.success("Club budget added successfully!")
            st.rerun()
        else:
            st.error("This category already has a budget for this club.")
st.divider()
st.subheader("Club Budget Overview")

budgets = get_club_budgets(club_id)

for budget in budgets:
    budget_id = budget[0]
    category = budget[1]
    budget_limit = budget[2]

    st.write(f"**{category}**")
    st.write(f"Current Budget: RM {budget_limit:.2f}")

    if role == "Treasurer":

        # Update Budget
        new_budget = st.number_input(
            f"New Budget for {category} (RM)",
            min_value=0.01,
            value=float(budget_limit),
            step=10.00,
            key=f"budget_{budget_id}"
        )

        if st.button("Update Budget", key=f"update_{budget_id}"):
            if new_budget != budget_limit:
                success = update_club_budget(
                    club_id, category, new_budget
                )

                if success:
                    st.success("Budget updated successfully!")
                    st.rerun()
            else:
                st.info("No changes were made.")

        # Delete Budget
        if st.button("Delete Budget", key=f"delete_{budget_id}"):
            success = delete_club_budget(club_id, category)

            if success:
                st.success("Budget deleted successfully!")
                st.rerun()
            else:
                st.error("Unable to delete budget.")
        else:
             st.info("No club budgets have been created yet.")
