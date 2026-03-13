"""Configuration helpers for loading environment variables and clients.

This centralizes loading .env and provides simple helper functions
to retrieve required variables and to create service clients.
"""
from dotenv import load_dotenv
import os

load_dotenv()


def get_env_var(name, default=None, required=False):
    """Return environment variable value.

    If required is True and the variable is missing/empty, raise RuntimeError.
    """
    val = os.getenv(name, default)
    if required and (val is None or val == ""):
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


def get_supabase_client():
    """Create and return a Supabase client using SUPABASE_URL and SUPABASE_KEY.

    Raises RuntimeError if credentials are not set.
    """
    from supabase import create_client

    url = get_env_var("SUPABASE_URL", required=True)
    key = get_env_var("SUPABASE_KEY", required=True)
    return create_client(url, key)
