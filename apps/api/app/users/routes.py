from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin_token
from app.core.database import get_db
from app.users.schemas import SyncUserRequest, SyncUserResponse
from app.users.service import ensure_user_workspace

router = APIRouter(prefix="/v1/internal", tags=["internal-users"])


@router.post("/sync-user", response_model=SyncUserResponse)
def sync_user(
    payload: SyncUserRequest,
    _admin: None = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> SyncUserResponse:
    synced = ensure_user_workspace(
        db,
        clerk_id=payload.clerk_id,
        email=str(payload.email),
        name=payload.name,
    )
    return SyncUserResponse(
        user_id=synced.user.id,
        clerk_id=synced.user.clerk_id,
        organization_id=synced.organization.id,
        current_project_id=synced.project.id,
        created=synced.created,
    )
