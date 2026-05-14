from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.api_keys.models import ApiKey
    from app.organizations.models import Organization
    from app.usage.models import UsageEvent


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        index=True,
    )
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    monthly_quota: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organization: Mapped[Organization] = relationship(back_populates="projects")
    api_keys: Mapped[list[ApiKey]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    usage_events: Mapped[list[UsageEvent]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
