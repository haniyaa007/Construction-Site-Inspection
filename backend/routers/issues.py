from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.database import get_db

router = APIRouter(prefix="/issues", tags=["issues"])


@router.post("", response_model=schemas.IssueRead, status_code=201)
def create_issue(payload: schemas.IssueCreate, db: Session = Depends(get_db)):
    if db.get(models.Inspection, payload.inspection_id) is None:
        raise HTTPException(status_code=404, detail="Inspection not found")

    if payload.detection_id is not None:
        detection = db.get(models.Detection, payload.detection_id)
        # The detection must exist AND belong to this same inspection
        if detection is None or detection.inspection_id != payload.inspection_id:
            raise HTTPException(status_code=404, detail="Detection not found in this inspection")

    issue = models.Issue(**payload.model_dump())
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@router.get("", response_model=list[schemas.IssueRead])
def list_issues(
    inspection_id: int | None = None,
    status: schemas.IssueStatus | None = None,
    severity: schemas.Severity | None = None,
    db: Session = Depends(get_db),
):
    query = select(models.Issue).order_by(models.Issue.id.desc())
    if inspection_id is not None:
        query = query.where(models.Issue.inspection_id == inspection_id)
    if status is not None:
        query = query.where(models.Issue.status == status)
    if severity is not None:
        query = query.where(models.Issue.severity == severity)
    return db.scalars(query).all()


@router.get("/{issue_id}", response_model=schemas.IssueRead)
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.get(models.Issue, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@router.patch("/{issue_id}", response_model=schemas.IssueRead)
def update_issue(issue_id: int, payload: schemas.IssueUpdate, db: Session = Depends(get_db)):
    issue = db.get(models.Issue, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    changes = payload.model_dump(exclude_unset=True)  # only fields the client actually sent
    for required_field in ("title", "severity", "status"):
        if required_field in changes and changes[required_field] is None:
            raise HTTPException(status_code=422, detail=f"{required_field} cannot be null")

    for field, value in changes.items():
        setattr(issue, field, value)
    db.commit()
    db.refresh(issue)
    return issue