import io

from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError

from backend.config import ALLOWED_FORMATS


def validate_image(data: bytes) -> tuple[str, int, int]:
    """Check the bytes are a real, allowed image. Returns (format, width, height)."""
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        with Image.open(io.BytesIO(data)) as img:
            img.verify()  # checks the file's integrity
        with Image.open(io.BytesIO(data)) as img:  # verify() invalidates the object
            image_format, (width, height) = img.format, img.size
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError):
        raise HTTPException(status_code=400, detail="File is not a valid image")

    if image_format not in ALLOWED_FORMATS:
        allowed = ", ".join(ALLOWED_FORMATS)
        raise HTTPException(
            status_code=415, detail=f"Unsupported image format. Allowed: {allowed}"
        )
    return image_format, width, height