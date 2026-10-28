"""
Initialisation et accès au client Supabase (Singleton).
"""

from typing import Optional
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """Retourne l'instance unique du client Supabase."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client
