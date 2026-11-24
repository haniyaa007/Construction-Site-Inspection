from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import config, models, schemas
from backend.database import get_db
from backend.services import storage
from backend.services.validation import validate_image

router = APIRouter(prefix="/inspections", tags=["uploads"])


@router.post("/{inspection_id}/upload", response_model=schemas.ImageRead, status_code=201)
def upload_image(
    inspection_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    upload_dir: Path = Depends(storage.get_upload_dir),
):
    inspection = db.get(models.Inspection, inspection_id)
    if inspection is None:
        raise HTTPException(status_code=404, detail="Inspection not found")

    # Read at most limit+1 bytes: enough to detect "too big" without loading it all
    data = file.file.read(config.MAX_UPLOAD_BYTES + 1)
    if len(data) > config.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large")

    image_format, width, height = validate_image(data)
    extension, mime_type = config.ALLOWED_FORMATS[image_format]

    stored_filename = storage.save_image(data, extension, upload_dir)
    try:
        image = models.Image(
            inspection_id=inspection_id,
            original_filename=Path(file.filename or "unnamed").name[:255],
            stored_filename=stored_filename,
            content_type=mime_type,
            size_bytes=len(data),
            width=width,
            height=height,
        )
        db.add(image)
        if inspection.status == "created":
            inspection.status = "uploaded"
        db.commit()
    except Exception:
        # Don't leave an orphan file on disk if the database write fails
        storage.delete_image(stored_filename, upload_dir)
        raise
    db.refresh(image)
    return image


@router.get("/{inspection_id}/images", response_model=list[schemas.ImageRead])
def list_images(inspection_id: int, db: Session = Depends(get_db)):
    if db.get(models.Inspection, inspection_id) is None:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return db.scalars(
        select(models.Image)
        .where(models.Image.inspection_id == inspection_id)
        .order_by(models.Image.id)
    ).all()