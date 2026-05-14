from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api_keys.schemas import ApiKeyCreate, ApiKeyCreated
from app.api_keys.service import create_api_key
from app.core.database import get_db
from app.projects.models import Project

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("", response_model=ApiKeyCreated, status_code=201)
def issue_api_key(payload: ApiKeyCreate, db: Session = Depends(get_db)) -> ApiKeyCreated:
    project = db.get(Project, str(payload.project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    api_key, raw_key = create_api_key(db, project_id=str(payload.project_id), name=payload.name)
    return ApiKeyCreated(
        id=api_key.id,
        project_id=api_key.project_id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        api_key=raw_key,
    )
