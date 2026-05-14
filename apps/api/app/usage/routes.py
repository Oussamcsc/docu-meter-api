from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.projects.models import Project
from app.usage.schemas import UsageSummary
from app.usage.service import get_project_usage_summary

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("/projects/{project_id}", response_model=UsageSummary)
def project_usage(project_id: UUID, db: Session = Depends(get_db)) -> UsageSummary:
    project = db.get(Project, str(project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    events, units = get_project_usage_summary(db, project_id=str(project_id))
    return UsageSummary(project_id=project_id, events=events, units=units)
