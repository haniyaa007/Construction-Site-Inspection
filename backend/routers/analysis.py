from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.database import get_db
from backend.services import detection, storage

router = APIRouter(prefix="/inspections", tags=["analysis"])


@router.post("/{inspection_id}/analyze", response_model=schemas.AnalysisSummary)
def analyze_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    upload_dir: Path = Depends(storage.get_upload_dir),
    detector: detection.Detector = Depends(detection.get_detector),
):
    inspection = db.get(models.Inspection, inspection_id)
    if inspection is None:
        raise HTTPException(status_code=404, detail="Inspection not found")
    if inspection.status == "analyzed":
        raise HTTPException(status_code=409, detail="Inspection has already been analyzed")

    images = db.scalars(
        select(models.Image)
        .where(models.Image.inspection_id == inspection_id)
        .order_by(models.Image.id)
    ).all()
    if not images:
        raise HTTPException(status_code=409, detail="Upload at least one image before analyzing")

    # Run the model on every image BEFORE touching the database,
    # so a failure halfway leaves nothing half-saved.
    rows = []
    for image in images:
        path = upload_dir / image.stored_filename
        if not path.exists():
            raise HTTPException(status_code=500, detail=f"Stored file for image {image.id} is missing")
        for found in detector.detect(path):
            rows.append(
                models.Detection(
                    inspection_id=inspection_id,
                    image_id=image.id,
                    object_class=found.object_class,
                    confidence=found.confidence,
                    x1=found.x1, y1=found.y1, x2=found.x2, y2=found.y2,
                    is_flagged=detection.is_flagged(found.object_class, found.confidence),
                )
            )

    db.add_all(rows)
    inspection.status = "analyzed"
    db.commit()

    return schemas.AnalysisSummary(
        inspection_id=inspection_id,
        status=inspection.status,
        images_analyzed=len(images),
        detections_total=len(rows),
        flagged_total=sum(row.is_flagged for row in rows),
    )


@router.get("/{inspection_id}/results", response_model=list[schemas.DetectionRead])
def get_results(
    inspection_id: int,
    flagged_only: bool = False,
    review_status: str | None = None,
    db: Session = Depends(get_db),
):
    if db.get(models.Inspection, inspection_id) is None:
        raise HTTPException(status_code=404, detail="Inspection not found")

    query = select(models.Detection).where(models.Detection.inspection_id == inspection_id)
    if flagged_only:
        query = query.where(models.Detection.is_flagged.is_(True))
    if review_status is not None:
        query = query.where(models.Detection.review_status == review_status)
    query = query.order_by(models.Detection.image_id, models.Detection.confidence.desc())
    return db.scalars(query).all()