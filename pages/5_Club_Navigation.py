
import streamlit as st

from database import (
    get_user_id,
    join_club,
    get_user_clubs,
    create_club
)

from navigation import show_finance_sidebar,show_custom_style


# ==================================
# 1. PAGE CONFIGURATION
# ==================================

st.set_page_config(
    page_title="Club Navigation",
    page_icon="🏢",
    layout="wide"
)


#2 sidebar

show_finance_sidebar()
#design
show_custom_style()

# ==================================
# 3. LOGIN CHECK
# ==================================

if not st.session_state.get("logged_in", False):
    st.warning("Please log in first.")
    st.switch_page("pages/0_Account.py")
    st.stop()
user_id = get_user_id(st.session_state.username)

# ==================================
# 4. PAGE TITLE and create club
# ==================================

st.title("🏢 Club Finance")
st.write("Select a club and choose a page to continue.")
st.divider()
st.divider()
st.subheader("Create a New Club")

with st.expander("Create Club"):
    new_club_name = st.text_input(
        "Club Name",
        key="new_club_name"
    )

    if st.button("Create Club", key="create_club"):

        if not new_club_name.strip():
            st.warning("Please enter a club name.")

        else:
            try:
                club_id, invitation_code = create_club(
                    new_club_name.strip(),
                    user_id
                )

                st.session_state.selected_club_id = club_id
                st.session_state.selected_club_name = new_club_name.strip()

                st.success("Club created successfully!")
                st.write(f"**Invitation Code:** {invitation_code}")

                st.rerun()

            except Exception as e:
                st.error(f"Unable to create club: {e}")

st.divider()

# ==================================
# 5. JOIN A CLUB
# ==================================

st.subheader("Join a Club")

invitation_code = st.text_input(
    "Enter Invitation Code"
)

if st.button("Join Club"):

    if not invitation_code.strip():

        st.warning("Please enter an invitation code.")

    else:

        user_id = get_user_id(
            st.session_state.username
        )

        result = join_club(
            invitation_code,
            user_id
        )

        if result == "success":

            st.success(
                "You have successfully joined the club!"
            )

            st.rerun()

        elif result == "invalid":

            st.error("Invalid invitation code.")

        elif result == "already_joined":

            st.warning(
                "You have already joined this club."
            )


st.divider()


# ==================================
# 6. MY CLUBS
# ==================================

st.subheader("My Clubs")

user_id = get_user_id(
    st.session_state.username
)

clubs = get_user_clubs(user_id)


if clubs:

    club_options = {
        club[1]: club[0]
        for club in clubs
    }

    selected_club = st.selectbox(
        "Select a Club",
        options=list(club_options.keys())
    )

    selected_club_id = club_options[selected_club]

    st.session_state.selected_club_id = selected_club_id
    st.session_state.selected_club_name = selected_club

    st.success(
        f"Currently selected: {selected_club}"
    )


    # ==================================
    # 7. CLUB PAGE NAVIGATION
    # ==================================

    
st.divider()

st.title(f"📂 {selected_club} Management")
st.write("Choose a feature to manage your club's finances.")

# First row
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("📊 Dashboard")
        st.caption("View financial overview and insights.")

        if st.button("Open Dashboard", key="club_dashboard",
                     use_container_width=True):
            st.switch_page("app.py")

with col2:
    with st.container(border=True):
        st.subheader("💰 Budget Setting")
        st.caption("Allocate and manage club budgets.")

        if st.button("Open Budget Setting", key="club_budget",
                     use_container_width=True):
            st.switch_page("pages/6_Club_Budget_Setting.py")

# Second row
col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.subheader("📋 Expense History")
        st.caption("Review all submitted expenses.")

        if st.button("View Expense History", key="club_history",
                     use_container_width=True):
            st.switch_page("pages/7_Club_Expense_History.py")

with col4:
    with st.container(border=True):
        st.subheader("✅ Expense Approval")
        st.caption("Review and approve pending expenses.")

        if st.button("Manage Approvals", key="club_approval",
                     use_container_width=True):
            st.switch_page("pages/8_Club-Expense_Approval.py")
#third row
with st.container(border=True):
    st.subheader("📝 Expense Submission")
    st.caption("Submit expenses and upload receipts.")

    if st.button("Submit an Expense", key="club_submission",
                 use_container_width=True):
        st.switch_page("pages/9_Club_Expense_Submission.py")
#fourth row

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #E9E1FF, #F5F0FF);
        padding: 22px;
        border-radius: 15px;
        border: 1px solid #D8C8F5;
        min-height: 190px;
    ">
        <div style="font-size: 30px;">📅</div>
        <h3 style="color: #59438C;">
            Programme Management
        </h3>
        <p style="color: #68568A;">
            Manage programme registrations,
            participant deposits and payment collection.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "💳 Open Programme Deposit",
        key="programme_deposit",
        use_container_width=True
    ):
        st.switch_page("pages/11_programme_deposit.py")