import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".zip", ".docx"}


def _storage_root() -> Path:
    root = Path(settings.storage_path)
    root.mkdir(parents=True, exist_ok=True)
    return root


def validate_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Extensao nao permitida: {suffix}")
    return suffix


async def save_file(file: UploadFile, subfolder: str) -> str:
    validate_extension(file.filename or "arquivo.bin")
    folder = _storage_root() / subfolder
    folder.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename or "upload").name
    stored_name = f"{uuid.uuid4().hex}_{safe_name}"
    target = folder / stored_name
    content = await file.read()
    target.write_bytes(content)
    return str(target.relative_to(_storage_root())).replace("\\", "/")


def delete_file(filepath: str) -> None:
    target = _storage_root() / filepath
    if target.is_file():
        target.unlink()


def resolve_path(filepath: str) -> Path:
    return _storage_root() / filepath


def get_file_url(filepath: str) -> str:
    return f"/api/v1/documentos/files/{filepath}"
