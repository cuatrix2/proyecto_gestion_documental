# db_configuration.py

import os
from supabase import create_client, Client # Ensure this is supabase-py v2 or later

# Supabase client initialization
# It's STRONGLY recommended to load credentials from environment variables or a config file
# rather than hardcoding them in the source code for security reasons.
SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "https://fonles-drive.fonlescompany.com") # Example fallback
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc0ODAzMTI0MCwiZXhwIjo0OTAzNzA0ODQwLCJyb2xlIjoic2VydmljZV9yb2xlIn0.2E8HXYZUIIQMYFI_oNx62asgb9PhmbarSlUSpU-ySsQ") # Example fallback

client_supabase: Client | None = None # Initialize with type hint for Client or None

if not SUPABASE_URL or not SUPABASE_KEY:
    # Handle missing configuration appropriately in a real application
    print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set as environment variables (checked in db_configuration.py).")
    # In a Django context, you might want to raise ImproperlyConfigured here
    # from django.core.exceptions import ImproperlyConfigured
    # raise ImproperlyConfigured("SUPABASE_URL and SUPABASE_KEY must be set for Supabase client initialization.")
else:
    try:
        client_supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        # You could add a print statement here if you want to confirm initialization during server start
        # print("Supabase client initialized successfully from db_configuration.py")
    except Exception as e:
        print(f"Error initializing Supabase client in db_configuration.py: {e}")
        client_supabase = None # Ensure it's None on failure

# You can also define a function to get the client if you prefer more control
# def get_supabase_client():
#     global client_supabase
#     # Add logic here if you need to re-initialize or check status
#     return client_supabase