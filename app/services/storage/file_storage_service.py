

from ...core.config import settings
from .local_storage import LocalStorageService
from .supabase_storage import SupabaseStorageService


def get_file_storage_service():
    provider = settings.STORAGE_PROVIDER.lower()

    if provider == "local":
        return LocalStorageService()

    if provider == "supabase":
        return SupabaseStorageService()



    raise ValueError(f"Unsupported storage provider: {provider}")