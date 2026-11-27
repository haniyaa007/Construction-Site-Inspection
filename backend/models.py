from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    location: Mapped[str | None] = mapped_column(String(300), default=None)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    inspections: Mapped[list["Inspection"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    date: Mapped[datetime] = mapped_column(default=utcnow)
    status: Mapped[str] = mapped_column(String(20), default="created")

    project: Mapped["Project"] = relationship(back_populates="inspections")
   
    images: Mapped[list["Image"]] = relationship(
    back_populates="inspection", cascade="all, delete-orphan"
    )
    detections: Mapped[list["Detection"]] = relationship(
    back_populates="inspection", cascade="all, delete-orphan"
    )
class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)
    inspection_id: Mapped[int] = mapped_column(ForeignKey("inspections.id"))
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_filename: Mapped[str] = mapped_column(String(100), unique=True)
    content_type: Mapped[str] = mapped_column(String(50))
    size_bytes: Mapped[int]
    width: Mapped[int]
    height: Mapped[int]
    uploaded_at: Mapped[datetime] = mapped_column(default=utcnow)

    inspection: Mapped["Inspection"] = relationship(back_populates="images")
    detections: Mapped[list["Detection"]] = relationship(
    back_populates="image", cascade="all, delete-orphan"
    )

class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(primary_key=True)
    inspection_id: Mapped[int] = mapped_column(ForeignKey("inspections.id"))
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"))
    object_class: Mapped[str] = mapped_column(String(50))
    confidence: Mapped[float]
    x1: Mapped[float]
    y1: Mapped[float]
    x2: Mapped[float]
    y2: Mapped[float]
    is_flagged: Mapped[bool] = mapped_column(default=False)
    review_status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    inspection: Mapped["Inspection"] = relationship(back_populates="detections")
    image: Mapped["Image"] = relationship(back_populates="detections")