from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.database import get_db

router = APIRouter(prefix="/inspections", tags=["inspections"])


@router.post("", response_model=schemas.InspectionRead, status_code=201)
def create_inspection(payload: schemas.InspectionCreate, db: Session = Depends(get_db)):
    if db.get(models.Project, payload.project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    inspection = models.Inspection(project_id=payload.project_id)
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection


@router.get("", response_model=list[schemas.InspectionRead])
def list_inspections(project_id: int | None = None, db: Session = Depends(get_db)):
    query = select(models.Inspection).order_by(models.Inspection.id.desc())
    if project_id is not None:
        query = query.where(models.Inspection.project_id == project_id)
    return db.scalars(query).all()


@router.get("/{inspection_id}", response_model=schemas.InspectionRead)
def get_inspection(inspection_id: int, db: Session = Depends(get_db)):
    inspection = db.get(models.Inspection, inspection_id)
    if inspection is None:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection