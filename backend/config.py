from pathlib import Path

UPLOAD_DIR = Path("uploads")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

# Pillow format name -> (file extension, MIME type)
ALLOWED_FORMATS = {
    "JPEG": (".jpg", "image/jpeg"),
    "PNG": (".png", "image/png"),
}

MODEL_PATH = Path("models/ppe.pt")

DETECTION_MIN_CONFIDENCE = 0.25  # store everything the model reports above this
FLAG_MIN_CONFIDENCE = 0.40       # raise a flag only above this
FLAGGED_CLASSES = {"NO-Hardhat", "NO-Safety Vest"}