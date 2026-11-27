from datetime import datetime

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