import secrets
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.api_keys.models import ApiKey
from app.core.config import get_settings
from app.core.security import api_key_digest_matches, digest_api_key


@dataclass(frozen=True)
class GeneratedApiKey:
    raw_key: str
    prefix: str
    key_digest: str


def generate_api_key() -> GeneratedApiKey:
    settings = get_settings()
    token = secrets.token_urlsafe(32)
    raw_key = f"{settings.api_key_prefix}_{token}"
    prefix = raw_key[:12]
    return GeneratedApiKey(raw_key=raw_key, prefix=prefix, key_digest=digest_api_key(raw_key))


def create_api_key(db: Session, *, project_id: str, name: str) -> tuple[ApiKey, str]:
    generated = generate_api_key()
    api_key = ApiKey(
        project_id=project_id,
        name=name,
        key_prefix=generated.prefix,
        key_digest=generated.key_digest,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key, generated.raw_key


def authenticate_api_key(db: Session, raw_key: str) -> ApiKey | None:
    key_prefix = raw_key[:12]
    candidates = db.query(ApiKey).filter(ApiKey.key_prefix == key_prefix, ApiKey.is_active.is_(True)).all()
    for api_key in candidates:
        if api_key_digest_matches(raw_key, api_key.key_digest):
            return api_key
    return None
