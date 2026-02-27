from supabase import create_client, Client
from app.core.config import settings

def get_supabase() -> Client:
    """
    Retorna o client oficial do Supabase. 
    Idealmente usando Service Role Key para interações backend-to-backend ou operações root, 
    especialmente quando precisamos criar tenants e gerenciar tudo no nível admin.
    """
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return supabase
