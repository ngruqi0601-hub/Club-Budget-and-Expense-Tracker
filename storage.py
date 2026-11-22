import streamlit as st
from supabase import create_client

# Connect to Supabase
def get_supabase_client():
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]

    supabase = create_client(
        supabase_url,
        supabase_key
    )

    return supabase