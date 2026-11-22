import smtplib
import streamlit as st
with smtplib.SMTP_SSL(
    "smtp.gmail.com",
    465,
    timeout=30
) as server:

    server.login(
        st.secrets["email"]["sender"],
        st.secrets["email"]["app_password"]
    )

    st.success("Gmail login successful!")