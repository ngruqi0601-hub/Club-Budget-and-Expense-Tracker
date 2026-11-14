from narwhals import nth
import streamlit as st
import pandas as pd
from database import create_club,get_user_id,join_club,get_user_clubs,get_total_club_budget,get_total_club_expenses,get_remaining_club_budget,get_category_expense_totals,get_club_budgets
if not st.session_state.get("logged_in",False):
    st.warning("Please log in to access this page.")
    st.switch_page("pages/0_Account.py")
if st.button("Log Out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.switch_page("pages/0_Account.py")

st.set_page_config(
    page_title="Club Budget Tracker",
    page_icon="💰",
    layout="wide"
)
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
    display: none;
}
    .stApp {
        background-color: #F8F5FF!important;
    }

    h1 {
        color: #8156C5!important;
    }

    h2, h3 {
        color: #A05ACB!important;
    }
    /* First dashboard card */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stMetric"] {
    background-color: #E9E1FF;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
}

/* Second dashboard card */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stMetric"] {
    background-color: #FFE4EB;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
}

/* Third dashboard card */
div[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetric"] {
    background-color: #DDF5EE;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    transition: 0.3s ease;
}
.stButton > button {
    width: 100% !important;
    background-color: #8156C5 !important;
    color: white !important;
    border-radius: 12px;
    border: none;
    padding: 10px 25px;
    font-weight: bold;
    font-size: 20px !important;
    transition: all 0.3s ease;
}
.stButton > button p {
    font-size: 20px !important;
}

.stButton > button:hover {
    background-color: #946FD0 !important;
    color: white !important;
    transform: translateY(-3px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}
.stApp h1, .stApp h2, .stApp h3{
    margin-bottom: 20px;
}

.stApp [data-testid="stMarkdownContainer"] p {
    line-height: 1.6;
}
    </style>
    """, unsafe_allow_html=True)


st.title("Club Budget and Expense Tracker")
st.write("Welcome to our club financial management system!")

st.subheader("Join a Club")

invitation_code = st.text_input("Enter Invitation Code")

if st.button("Join Club"):
    if not invitation_code.strip():
        st.warning("Please enter an invitation code.")

    else:
        user_id = get_user_id(st.session_state.username)

        result = join_club(invitation_code, user_id)

        if result == "success":
            st.success("You have successfully joined the club!")

        elif result == "invalid":
            st.error("Invalid invitation code.")

        elif result == "already_joined":
            st.warning("You have already joined this club.")


# My Clubs
st.subheader("My Clubs")

user_id = get_user_id(st.session_state.username)
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

    club_id = club_options[selected_club]
    st.session_state.selected_club_id = club_id

    st.success(f"Currently managing: {selected_club}")

    # Club Financial Dashboard
    st.divider()
    st.subheader("Club Financial Dashboard")

    total_budget = get_total_club_budget(club_id)
    total_expenses = get_total_club_expenses(club_id)
    remaining_budget = get_remaining_club_budget(club_id)
    if total_budget > 0:
       remaining_percentage = (remaining_budget / total_budget) * 100
    else:
       remaining_percentage = 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Budget", f"RM {total_budget:.2f}")

    with col2:
        st.metric("Total Expenses", f"RM {total_expenses:.2f}")

    with col3:
        st.metric(
    "Remaining Budget",
    f"RM {remaining_budget:.2f}",
    delta=f"{remaining_percentage:.1f}% remaining"
)
    # Club Budget Usage
    st.divider()
    st.subheader("Club Budget Usage")

    if total_budget > 0:

        usage = total_expenses / total_budget

        st.progress(min(usage, 1.0))
        st.write(f"Budget Used: {usage * 100:.1f}%")
        if usage > 1:
           st.error("Club expenses have exceeded the total budget!")

        elif usage >= 0.8:
            st.warning(
              "Attention! The club has used at least 80% of its budget."
    )

        else:
            st.success("Club spending is within a healthy range.")
    
    
            

    else:
        st.info("No club budget has been set yet.")

    # Category Budget Analysis
    st.divider()
    st.subheader("Category Budget Analysis")

    budgets = get_club_budgets(club_id)
    category_expenses = get_category_expense_totals(club_id)

    budget_dict = {
        budget[1]: budget[2]
        for budget in budgets
    }

    expense_dict = {
        category: amount
        for category, amount in category_expenses
    }

    # Approved Expenses Pie Chart
    st.write("**Approved Expenses Distribution**")

    if category_expenses:

        chart_data = pd.DataFrame(
            category_expenses,
            columns=["Category", "Amount"]
        )

        st.vega_lite_chart(
            chart_data,
            {
                "mark": {
                    "type": "arc",
                    "innerRadius": 50
                },
                "encoding": {
                    "theta": {
                        "field": "Amount",
                        "type": "quantitative"
                    },
                    "color": {
                        "field": "Category",
                        "type": "nominal"
                    },
                    "tooltip": [
                        {
                            "field": "Category",
                            "type": "nominal"
                        },
                        {
                            "field": "Amount",
                            "type": "quantitative"
                        }
                    ]
                }
            },
            use_container_width=True
        )

    else:
        st.info("No approved expenses available for the chart.")

    # Category Budget Breakdown
    st.divider()
    st.write("**Budget Breakdown by Category**")

    all_categories = sorted(
        set(budget_dict) | set(expense_dict)
    )

    category_rows = []

    for category in all_categories:

        budget_limit = budget_dict.get(category, 0)
        spent = expense_dict.get(category, 0)
        remaining = budget_limit - spent

        if category not in budget_dict:
            status = "No Budget Allocated"

        elif remaining < 0:
            status = "Over Budget"

        else:
            status = "Within Budget"

        category_rows.append({
            "Category": category,
            "Budget (RM)": round(budget_limit, 2),
            "Approved Expenses (RM)": round(spent, 2),
            "Remaining (RM)": round(remaining, 2),
            "Status": status
        })

    if category_rows:

        category_df = pd.DataFrame(category_rows)

        st.dataframe(
            category_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No category budgets or approved expenses yet.")
    # Financial Insights
    st.divider()
    st.subheader("Financial Insights")

    if category_expenses:

        highest_category = max(
            category_expenses,
            key=lambda item: item[1]
        )
    # Category with the lowest remaining budget
    if category_rows:

        lowest_category = min(
            category_rows,
            key=lambda item: item["Remaining (RM)"]
        )

        st.info(
            f"Lowest remaining budget: {lowest_category['Category']} "
            f"(RM {lowest_category['Remaining (RM)']:.2f})"
        )
        st.info(
            f"Highest spending category: {highest_category[0]} "
            f"(RM {highest_category[1]:.2f})"
        )

    if total_budget > 0 and total_expenses > total_budget:
        st.warning("The club has exceeded its overall budget.")

    elif total_budget > 0:
        st.success("The club is currently within its overall budget.")
else:
    st.info("You haven't joined any clubs yet.")



st.subheader("Financial Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Budget", "Not set")

with col2:
    st.metric("Total Expenses", "No expenses yet")

with col3:
    st.metric("Remaining Budget", "Not available")

st.subheader("Main Features")

st.write("1. Record income and expense")
st.write("2. Monitor event budgets")
st.write("3. View financial history")
st.write("4. Receive budget alerts")

if st.button("Next"):
    st.switch_page("pages/1_Expense_Entry.py")