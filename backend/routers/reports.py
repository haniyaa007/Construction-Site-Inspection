from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.database import get_db
from backend.services import reporting

router = APIRouter(prefix="/reports", tags=["reports"])


def _analyzed_inspection(db: Session, inspection_id: int) -> models.Inspection:
    inspection = db.get(models.Inspection, inspection_id)
    if inspection is None:
        raise HTTPException(status_code=404, detail="Inspection not found")
    if inspection.status != "analyzed":
        raise HTTPException(status_code=409, detail="Inspection has not been analyzed yet")
    return inspection


@router.get("/{inspection_id}", response_model=schemas.ReportRead)
def get_report(inspection_id: int, db: Session = Depends(get_db)):
    return reporting.build_report(db, _analyzed_inspection(db, inspection_id))


@router.get("/{inspection_id}/markdown", response_class=PlainTextResponse)
def get_report_markdown(inspection_id: int, db: Session = Depends(get_db)):
    report = reporting.build_report(db, _analyzed_inspection(db, inspection_id))
    return PlainTextResponse(reporting.render_markdown(report), media_type="text/markdown")