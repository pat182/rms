from uuid import uuid4
import asyncio
from urllib.parse import urlparse, unquote

from app.core.config import settings

from fastapi import HTTPException, UploadFile
from supabase import create_client


class SupabaseStorageService:
    def __init__(
        self,
        max_file_size: int = 5 * 1024 * 1024,
        allowed_content_types: dict[str, str] | None = None,
    ):
        self.max_file_size = max_file_size

        self.allowed_content_types = allowed_content_types or {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }

        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )

        self.bucket = settings.SUPABASE_STORAGE_BUCKET

    async def save_image(
        self,
        file: UploadFile,
        folder: str = "menu-items",
    ) -> str:
        if file.content_type not in self.allowed_content_types:
            raise HTTPException(
                status_code=400,
                detail="Only JPEG, PNG, and WebP images are allowed.",
            )

        if (
            not folder
            or "/" in folder
            or "\\" in folder
            or folder in {".", ".."}
        ):
            raise ValueError("Invalid upload folder.")

        filename = (
            f"{uuid4().hex}"
            f"{self.allowed_content_types[file.content_type]}"
        )

        storage_path = f"{folder}/{filename}"
        size = 0
        image_data = bytearray()

        try:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)

                if size > self.max_file_size:
                    raise HTTPException(
                        status_code=413,
                        detail="Image must not exceed the size limit.",
                    )

                image_data.extend(chunk)

            if size == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded image is empty.",
                )

            await asyncio.to_thread(
                lambda: self.client.storage
                .from_(self.bucket)
                .upload(
                    path=storage_path,
                    file=bytes(image_data),
                    file_options={
                        "content-type": file.content_type,
                        "upsert": "false",
                    },
                )
            )
            return self.client.storage.from_(self.bucket).get_public_url(storage_path)
            # return storage_path

        finally:
            await file.close()

    async def delete_image(self, image_url: str) -> None:
        if not image_url:
            return

        parsed_url = urlparse(image_url)

        prefix = f"/storage/v1/object/public/{self.bucket}/"

        if not parsed_url.path.startswith(prefix):
            return

        storage_path = unquote(parsed_url.path.removeprefix(prefix))

        if not storage_path or ".." in storage_path.split("/"):
            return

        # from app.core.logger import log_info
        # log_info("==================================")
        # log_info("FSS IMAGE_URL:", storage_path)
        # log_info("==================================")
        await asyncio.to_thread(
            lambda: self.client.storage
            .from_(self.bucket)
            .remove([storage_path])
        )