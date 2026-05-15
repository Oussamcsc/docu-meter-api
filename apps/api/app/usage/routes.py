from datetime import UTC, date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin_token
from app.core.database import get_db
from app.projects.models import Project
from app.usage.schemas import AdminUsageSummary, UsageSummary
from app.usage.service import get_project_usage_summary

router = APIRouter(prefix="/usage", tags=["usage"])
admin_router = APIRouter(prefix="/v1", tags=["admin-usage"])


def next_month_reset_date(today: date | None = None) -> date:
    current = today or datetime.now(UTC).date()
    if current.month == 12:
        return date(current.year + 1, 1, 1)
    return date(current.year, current.month + 1, 1)


@router.get("/projects/{project_id}", response_model=UsageSummary)
def project_usage(project_id: UUID, db: Session = Depends(get_db)) -> UsageSummary:
    project = db.get(Project, str(project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    events, units = get_project_usage_summary(db, project_id=str(project_id))
    return UsageSummary(project_id=project_id, events=events, units=units)


@admin_router.get("/usage", response_model=AdminUsageSummary)
def dashboard_usage(
    project_id: UUID,
    _admin: None = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> AdminUsageSummary:
    # Primary-key lookup uses the indexed projects.id column, keeping the dashboard query O(log n).
    project = db.get(Project, str(project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    percentage = 0.0
    if project.monthly_quota > 0:
        percentage = round((project.usage_count / project.monthly_quota) * 100, 2)

    return AdminUsageSummary(
        project_id=project_id,
        usage_count=project.usage_count,
        monthly_quota=project.monthly_quota,
        percentage=percentage,
        reset_date=next_month_reset_date(),
    )
