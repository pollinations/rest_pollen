import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
supabase_api_key: str = os.environ.get("SUPABASE_API_KEY")
supabase: Client = None
if url is not None and supabase_api_key is not None:
    supabase = create_client(url, supabase_api_key)
