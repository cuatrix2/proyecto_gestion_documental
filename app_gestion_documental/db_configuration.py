# db_configuration.py

import os
from supabase import create_client, Client 


SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "https://fonles-drive.fonlescompany.com") 
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc0ODAzMTI0MCwiZXhwIjo0OTAzNzA0ODQwLCJyb2xlIjoic2VydmljZV9yb2xlIn0.2E8HXYZUIIQMYFI_oNx62asgb9PhmbarSlUSpU-ySsQ") # Example fallback

client_supabase: Client | None = None 

if not SUPABASE_URL or not SUPABASE_KEY:
  
    print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set as environment variables (checked in db_configuration.py).")

else:
    try:
        client_supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    except Exception as e:
        print(f"Error initializing Supabase client in db_configuration.py: {e}")
        client_supabase = None # Ensure it's None on failure

