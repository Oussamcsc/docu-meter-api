from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.organizations.models import Organization
from app.projects.models import Project
from app.projects.schemas import ProjectCreate, ProjectRead

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    organization = db.get(Organization, str(payload.organization_id))
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    project = Project(
        organization_id=str(payload.organization_id),
        name=payload.name,
        monthly_quota=payload.monthly_quota,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
