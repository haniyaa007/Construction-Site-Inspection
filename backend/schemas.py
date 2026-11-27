from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    location: str | None = Field(default=None, max_length=300)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str | None
    created_at: datetime


class InspectionCreate(BaseModel):
    project_id: int


class InspectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    date: datetime
    status: str

class ImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inspection_id: int
    original_filename: str
    content_type: str
    size_bytes: int
    width: int
    height: int
    uploaded_at: datetime
class DetectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inspection_id: int
    image_id: int
    object_class: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float
    is_flagged: bool
    review_status: str
    created_at: datetime


class AnalysisSummary(BaseModel):
    inspection_id: int
    status: str
    images_analyzed: int
    detections_total: int
    flagged_total: int

Severity = Literal["low", "medium", "high", "critical"]
IssueStatus = Literal["open", "in_progress", "resolved"]
ReviewStatus = Literal["pending", "confirmed", "dismissed"]


class DetectionReview(BaseModel):
    review_status: ReviewStatus


class IssueCreate(BaseModel):
    inspection_id: int
    detection_id: int | None = None
    title: str = Field(min_length=1, max_length=200)
    severity: Severity
    description: str | None = Field(default=None, max_length=2000)
    assigned_to: str | None = Field(default=None, max_length=100)


class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    severity: Severity | None = None
    description: str | None = Field(default=None, max_length=2000)
    assigned_to: str | None = Field(default=None, max_length=100)
    status: IssueStatus | None = None


class IssueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inspection_id: int
    detection_id: int | None
    title: str
    severity: str
    description: str | None
    assigned_to: str | None
    status: str
    created_at: datetime
    updated_at: datetime