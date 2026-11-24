from pathlib import Path

UPLOAD_DIR = Path("uploads")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

# Pillow format name -> (file extension, MIME type)
ALLOWED_FORMATS = {
    "JPEG": (".jpg", "image/jpeg"),
    "PNG": (".png", "image/png"),
}