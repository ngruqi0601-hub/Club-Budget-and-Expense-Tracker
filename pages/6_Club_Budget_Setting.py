

import streamlit as st

from database import (
    add_club_budget,
    get_club_budgets,
    update_club_budget,
    delete_club_budget,
    get_user_club_role,
    get_user_id
)

from navigation import show_finance_sidebar,show_custom_style


# ==================================
# 1. PAGE CONFIGURATION
# ==================================

st.set_page_config(
    page_title="Club Budget Setting",
    page_icon="💰",
    layout="wide"
)


#2. sidebar
show_finance_sidebar()
#design
show_custom_style()


# ==================================
# 3. LOGIN CHECK
# ==================================

if (
    not st.session_state.get("logged_in", False)
    or not st.session_state.get("username")
):
    st.warning("Please log in to access this page.")
    st.switch_page("pages/0_Account.py")
    st.stop()


# ==================================
# 4. SELECTED CLUB CHECK
# ==================================

club_id = st.session_state.get("selected_club_id")

if club_id is None:

    st.warning("Please select a club first.")

    if st.button("Select Club"):
        st.switch_page("pages/5_Club_Navigation.py")

    st.stop()


club_name = st.session_state.get(
    "selected_club_name",
    "Selected Club"
)


# ==================================
# 5. USER AND MEMBERSHIP CHECK
# ==================================

user_id = get_user_id(st.session_state.username)

role = get_user_club_role(user_id, club_id)

if role is None:
    st.error("You are not a member of this club.")
    st.stop()


# ==================================
# 6. PAGE TITLE
# ==================================

st.title(f"💰 {club_name} Budget Setting")

st.write("Manage and monitor your club's allocated budgets.")

st.divider()


# ==================================
# 7. ADD NEW BUDGET
# ==================================

if role == "Treasurer":

    st.subheader("Add New Budget")

    all_categories = [
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

    existing_categories = [
        budget[1]
        for budget in get_club_budgets(club_id)
    ]

    available_categories = [
        category
        for category in all_categories
        if category not in existing_categories
    ]

    if available_categories:

        category = st.selectbox(
            "Select Category",
            available_categories
        )

        budget_limit = st.number_input(
            "Budget Limit (RM)",
            min_value=0.01,
            step=10.00
        )

        if "budget_success" not in st.session_state:
            st.session_state.budget_success = False

        if st.button("Add Budget"):

            success = add_club_budget(
                club_id,
                category,
                budget_limit
            )

            if success:
                st.session_state.budget_success = True
                st.rerun()

            else:
                st.error(
                    "This category already has a budget for this club."
                )

    else:
        st.success("All budget categories have been added!")

    if st.session_state.get("budget_success", False):
        st.success("Club budget added successfully!")
        st.session_state.budget_success = False

else:
    st.info("Only the Treasurer can manage club budgets.")


# ==================================
# 8. CLUB BUDGET OVERVIEW
# ==================================

st.divider()
st.subheader("Club Budget Overview")

budgets = get_club_budgets(club_id)


if budgets:

    # Calculate total budget once
    total_allocated = sum(
        budget[2] for budget in budgets
    )

    # Display total budget
    st.metric(
        "Total Allocated Budget",
        f"RM {total_allocated:.2f}"
    )

    st.divider()

    # Display individual category budgets
    for budget in budgets:

        budget_id = budget[0]
        category = budget[1]
        budget_limit = budget[2]

        st.write(f"**{category}**")
        st.write(f"Current Budget: RM {budget_limit:.2f}")

        # Budget Allocation Percentage
        if total_allocated > 0:

            allocation_percentage = (
                budget_limit / total_allocated
            ) * 100

            st.progress(allocation_percentage / 100)

            st.caption(
                f"{allocation_percentage:.1f}% "
                "of total club budget"
            )

        # UPDATE AND DELETE BUDGET
        if role == "Treasurer":

            with st.expander(f"✏️ Update {category} Budget"):

                new_budget = st.number_input(
                    "New Budget Limit (RM)",
                    min_value=0.01,
                    value=float(budget_limit),
                    step=10.00,
                    key=f"update_budget_{budget_id}"
                )

                if st.button(
                    "Save Changes",
                    key=f"save_budget_{budget_id}"
                ):
                    success = update_club_budget(
                            club_id,
                            category,
                            new_budget
                        )

                    if success:
                        st.success("Budget updated successfully!")
                        st.rerun()
                    else:
                        st.error("Unable to update budget.")

            if st.button(
                f"🗑️ Delete {category} Budget",
                key=f"delete_budget_{budget_id}"
            ):
                success = delete_club_budget(club_id, category)

                if success:
                    st.success("Budget deleted successfully!")
                    st.rerun()
                else:
                    st.error("Unable to delete budget.")

        st.divider()

else:
    st.info("No club budgets have been created yet.")


# PAGE NAVIGATION
col1, col2 = st.columns(2)

with col1:
    if st.button("⬅️ Back", use_container_width=True):
        st.switch_page("pages/5_Club_Navigation.py")

with col2:
    if st.button("Next ➡️", use_container_width=True):
        st.switch_page("pages/9_Club_Expense_Submission.py")
