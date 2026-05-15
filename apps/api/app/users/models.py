from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.organizations.models import Organization
    from app.projects.models import Project


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        index=True,
    )
    clerk_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    current_org_id: Mapped[str | None] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=True,
        index=True,
    )
    current_project_id: Mapped[str | None] = mapped_column(
        ForeignKey("projects.id"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    current_org: Mapped[Organization | None] = relationship(foreign_keys=[current_org_id])
    current_project: Mapped[Project | None] = relationship(foreign_keys=[current_project_id])
    organization_memberships: Mapped[list[OrganizationMembership]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"
    __table_args__ = (UniqueConstraint("user_id", "organization_id", name="uq_user_org_membership"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="owner")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="organization_memberships")
    organization: Mapped[Organization] = relationship(back_populates="user_memberships")
