from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.database import get_db

router = APIRouter(prefix="/detections", tags=["review"])


@router.patch("/{detection_id}/review", response_model=schemas.DetectionRead)
def review_detection(
    detection_id: int, payload: schemas.DetectionReview, db: Session = Depends(get_db)
):
    detection = db.get(models.Detection, detection_id)
    if detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    detection.review_status = payload.review_status
    db.commit()
    db.refresh(detection)
    return detection