import venv_ssl_patch  # <- must be first to patch ssl

from supabase import create_client

SUPABASE_URL = "https://lywnkinyjgokzytljwjl.supabase.co"
SUPABASE_KEY = "sb_publishable_NiiBllokNf-bWa993VVk6A_pX_fwzCL"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    resp = supabase.table("plants").select("id, name, last_watered").limit(1).execute()
    print("OK, got data:", resp.data)
except Exception as e:
    print("ERROR:", repr(e))