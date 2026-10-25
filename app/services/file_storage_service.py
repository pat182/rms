from pathlib import Path
from uuid import uuid4
import asyncio

import aiofiles
from fastapi import HTTPException, UploadFile


class FileStorageService:
    def __init__(
            self,
            upload_root: Path = Path("uploads"),
            max_file_size: int = 5 * 1024 * 1024,
            allowed_content_types: dict[str, str] | None = None,
    ):
        self.upload_root = upload_root
        self.max_file_size = max_file_size
        self.allowed_content_types = allowed_content_types or {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }

    async def save_image(self,file: UploadFile,folder: str = "menu-items") -> str:
        if file.content_type not in self.allowed_content_types:
            raise HTTPException(
                status_code=400,
                detail="Only JPEG, PNG, and WebP images are allowed.",
            )
        if (
                not folder
                or Path(folder).is_absolute()
                or len(Path(folder).parts) != 1
                or folder in {".", ".."}
        ):
            raise ValueError("Invalid upload folder.")

        upload_dir = self.upload_root / folder
        upload_dir.mkdir(parents=True, exist_ok=True)

        filename = (
            f"{uuid4().hex}"
            f"{self.allowed_content_types[file.content_type]}"
        )

        file_path = upload_dir / filename
        size = 0

        try:
            async with aiofiles.open(file_path, "wb") as output:
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)

                    if size > self.max_file_size:
                        raise HTTPException(
                            status_code=413,
                            detail="Image must not exceed the size limit.",
                        )

                    await output.write(chunk)

            if size == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded image is empty.",
                )

            return f"/uploads/{folder}/{filename}"

        except Exception:
            file_path.unlink(missing_ok=True)
            raise
        finally:
            await file.close()

    async def delete_image(self, image_url: str) -> None:
        prefix = "/uploads/"

        if not image_url.startswith(prefix):
            return

        relative_path = Path(image_url.removeprefix(prefix))

        if relative_path.is_absolute() or ".." in relative_path.parts:
            return

        upload_root = self.upload_root.resolve()
        file_path = (self.upload_root / relative_path).resolve()

        if not file_path.is_relative_to(upload_root):
            return

        await asyncio.to_thread(file_path.unlink, missing_ok=True)