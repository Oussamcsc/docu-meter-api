from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api_keys.models import ApiKey
from app.api_keys.schemas import (
    AdminApiKeyCreated,
    AdminApiKeyList,
    ApiKeyCreate,
    ApiKeyCreated,
    ApiKeyCreateForProject,
    ApiKeyRead,
)
from app.api_keys.service import create_api_key, mask_api_key, revoke_api_key
from app.auth.dependencies import require_admin_token
from app.core.database import get_db
from app.projects.models import Project

router = APIRouter(prefix="/api-keys", tags=["api-keys"])
admin_router = APIRouter(prefix="/v1", tags=["admin-api-keys"])


def serialize_api_key(api_key: ApiKey) -> ApiKeyRead:
    return ApiKeyRead(
        id=api_key.id,
        project_id=api_key.project_id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        is_active=api_key.is_active,
        masked_token=mask_api_key(api_key.key_prefix),
    )


@router.post("", response_model=ApiKeyCreated, status_code=201)
def issue_api_key(
    payload: ApiKeyCreate,
    _admin: None = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> ApiKeyCreated:
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


@admin_router.get("/keys", response_model=AdminApiKeyList)
def list_dashboard_api_keys(
    project_id: UUID,
    _admin: None = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> AdminApiKeyList:
    project = db.get(Project, str(project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    keys = (
        db.query(ApiKey)
        .filter(ApiKey.project_id == str(project_id))
        .order_by(ApiKey.created_at.desc())
        .all()
    )
    return AdminApiKeyList(project_id=project_id, keys=[serialize_api_key(key) for key in keys])


@admin_router.post("/keys", response_model=AdminApiKeyCreated, status_code=201)
def create_dashboard_api_key(
    payload: ApiKeyCreate,
    _admin: None = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> AdminApiKeyCreated:
    project = db.get(Project, str(payload.project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    api_key, raw_key = create_api_key(db, project_id=str(payload.project_id), name=payload.name)
    return AdminApiKeyCreated(
        id=api_key.id,
        project_id=api_key.project_id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        key=raw_key,
    )


@admin_router.post("/projects/{project_id}/keys", response_model=AdminApiKeyCreated, status_code=201)
def create_project_api_key(
    project_id: UUID,
    payload: ApiKeyCreateForProject,
    _admin: None = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> AdminApiKeyCreated:
    project = db.get(Project, str(project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    api_key, raw_key = create_api_key(db, project_id=str(project_id), name=payload.name)
    return AdminApiKeyCreated(
        id=api_key.id,
        project_id=api_key.project_id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        key=raw_key,
    )


@admin_router.delete("/projects/{project_id}/keys/{api_key_id}", response_model=ApiKeyRead)
def revoke_project_api_key(
    project_id: UUID,
    api_key_id: UUID,
    _admin: None = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> ApiKeyRead:
    api_key = db.get(ApiKey, str(api_key_id))
    if api_key is None or api_key.project_id != str(project_id):
        raise HTTPException(status_code=404, detail="API key not found")

    revoked = revoke_api_key(db, api_key=api_key)
    return serialize_api_key(revoked)
