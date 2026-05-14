from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api_keys.models import ApiKey
from app.core.database import get_db
from app.protected_api.dependencies import require_api_key
from app.usage.service import has_project_quota_remaining


def enforce_project_quota(
    api_key: ApiKey = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> None:
    if not has_project_quota_remaining(db, project_id=api_key.project_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Project monthly quota exceeded",
        )
