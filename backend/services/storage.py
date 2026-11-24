import uuid
from pathlib import Path

from backend.config import UPLOAD_DIR


def get_upload_dir() -> Path:
    """Dependency: lets tests swap in a temporary folder."""
    return UPLOAD_DIR


def save_image(data: bytes, extension: str, upload_dir: Path) -> str:
    """Write bytes to disk under a random name. Returns the stored filename."""
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid.uuid4().hex}{extension}"
    (upload_dir / stored_filename).write_bytes(data)
    return stored_filename


def delete_image(stored_filename: str, upload_dir: Path) -> None:
    (upload_dir / stored_filename).unlink(missing_ok=True)