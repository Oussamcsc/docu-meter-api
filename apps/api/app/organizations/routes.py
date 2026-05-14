from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.organizations.models import Organization
from app.organizations.schemas import OrganizationCreate, OrganizationRead

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationRead, status_code=201)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)) -> Organization:
    organization = Organization(name=payload.name)
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization
