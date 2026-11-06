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