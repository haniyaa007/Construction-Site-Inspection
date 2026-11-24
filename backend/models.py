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