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
import uuid
import os

# Upload receipt to Supabase Storage
def upload_receipt(receipt, club_id):

    supabase = get_supabase_client()

    file_extension = os.path.splitext(receipt.name)[1]

    file_name = f"{uuid.uuid4().hex}{file_extension}"

    file_path = f"{club_id}/{file_name}"

    supabase.storage.from_("receipts").upload(
        file_path,
        receipt.getvalue(),
        {
            "content-type": receipt.type,
            "upsert": "false"
        }
    )

    return file_path
# Download receipt from Supabase Storage
def download_receipt(file_path):
    try:
        supabase = get_supabase_client()

        response = supabase.storage.from_("receipts").download(
            file_path
        )

        return response

    except Exception as e:
        print(f"Receipt download error: {e}")
        return None