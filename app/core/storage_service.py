"""Storage service - supports local filesystem or Supabase Storage"""
import uuid
import os
import logging
from pathlib import Path
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class LocalStorageService:
    """Saves files to local filesystem and serves via /uploads static mount"""

    def upload_file(
        self, file_content: bytes, original_filename: str, folder: str = "documents"
    ) -> Optional[str]:
        try:
            upload_dir = Path("uploads") / folder
            upload_dir.mkdir(parents=True, exist_ok=True)

            ext = os.path.splitext(original_filename)[1]
            unique_filename = f"{uuid.uuid4()}{ext}"
            file_path = upload_dir / unique_filename

            with open(file_path, "wb") as f:
                f.write(file_content)

            # Return relative path — served via /uploads static mount
            relative_path = f"uploads/{folder}/{unique_filename}"
            logger.info(f"Fichier sauvegardé localement: {relative_path}")
            return relative_path

        except Exception as e:
            logger.error(f"Erreur sauvegarde locale: {e}")
            return None

    def delete_file(self, file_path: str) -> bool:
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
            return True
        except Exception as e:
            logger.error(f"Erreur suppression locale: {e}")
            return False


class SupabaseStorageService:
    """Uploads files to Supabase Storage and returns public URL"""

    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.bucket_name = settings.SUPABASE_BUCKET_NAME

    def _get_client(self):
        from supabase import create_client
        return create_client(self.supabase_url, self.supabase_key)

    def upload_file(
        self, file_content: bytes, original_filename: str, folder: str = "documents"
    ) -> Optional[str]:
        try:
            ext = os.path.splitext(original_filename)[1]
            unique_filename = f"{folder}/{uuid.uuid4()}{ext}"

            client = self._get_client()
            client.storage.from_(self.bucket_name).upload(
                path=unique_filename,
                file=file_content,
                file_options={"content-type": self._get_content_type(ext)}
            )

            public_url = client.storage.from_(self.bucket_name).get_public_url(
                unique_filename
            )
            logger.info(f"Fichier uploadé sur Supabase: {public_url}")
            return public_url

        except Exception as e:
            logger.error(f"Erreur upload Supabase: {e}")
            return None

    def delete_file(self, file_url: str) -> bool:
        try:
            marker = f"/object/public/{self.bucket_name}/"
            if marker not in file_url:
                return False
            file_path = file_url.split(marker)[-1]
            client = self._get_client()
            client.storage.from_(self.bucket_name).remove([file_path])
            return True
        except Exception as e:
            logger.error(f"Erreur suppression Supabase: {e}")
            return False

    @staticmethod
    def _get_content_type(extension: str) -> str:
        types = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".xls": "application/vnd.ms-excel",
        }
        return types.get(extension.lower(), "application/octet-stream")


def get_storage_service():
    """Factory — returns the active storage backend based on STORAGE_BACKEND setting"""
    backend = settings.STORAGE_BACKEND.lower()
    if backend == "supabase":
        return SupabaseStorageService()
    return LocalStorageService()


# Singleton
storage_service = get_storage_service()
