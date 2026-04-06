from supabase import create_client
import os

# Replace with your values
SUPABASE_URL = "https://lywnkinyjgokzytljwjl.supabase.co"  # From Project URL
SUPABASE_KEY = "sb_publishable_NiiBllokNf-bWa993VVk6A_pX_fwzCL"  # From Settings > API

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test read
response = supabase.table("plants").select("*").execute()
print("Plants from Supabase:", response.data)

import streamlit as st
print("URL:", st.secrets["SUPABASE_URL"])