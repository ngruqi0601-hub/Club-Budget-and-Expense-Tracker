import streamlit as st
st.title("Budget Setting")
if "budget" not in st.session_state:
    st.session_state.budget=0.0
budget=st.number_input(
    "Enter total budget(RM)",
    min_value=0.0,
    step=100.0
)
if st.button("Submit Budget",key="submit budget"):
    if budget<=0:
        st.warning("Please enter a value")
    else:
        st.session_state.budget=budget
        st.success("Budget submitted successfully!")
st.subheader("Current BUdget:RM"+str(st.session_state.budget))
if "expenses" not in st.session_state:
    st.session_state.expenses = []

total_expenses = sum(
    float(expense["Amount(RM)"])
    for expense in st.session_state.expenses
)
remaining_budget=st.session_state.budget-total_expenses
st.metric("Total Budget" , f"RM{st.session_state.budget:.2f}")
st.metric("Total Expenses", f"RM{total_expenses:.2f}")
st.metric("Remaining Budget", f"RM{remaining_budget:.2f}")
if remaining_budget < 0:
    st.error("You have exceeded your budget!")

elif remaining_budget == 0:
    st.warning("You have used your entire budget!")

else:
    st.success("You are within your budget!")
if st.session_state.budget > 0:
    spending_ratio = total_expenses / st.session_state.budget

    st.subheader("Budget Usage")
    st.progress(min(spending_ratio, 1.0))

    st.write(f"Budget Used: {spending_ratio * 100:.1f}%")