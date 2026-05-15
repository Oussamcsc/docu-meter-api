import hmac

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import get_settings

admin_token_header = APIKeyHeader(name="X-Admin-Token", auto_error=False)


def require_admin_token(token: str | None = Security(admin_token_header)) -> None:
    settings = get_settings()
    configured_token = settings.admin_api_token
    if configured_token is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin API token is not configured",
        )

    expected = configured_token.get_secret_value()
    if token is None or not hmac.compare_digest(token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token",
        )
