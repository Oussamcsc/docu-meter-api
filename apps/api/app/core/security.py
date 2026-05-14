import hmac
from hashlib import sha256

from app.core.config import get_settings


def digest_api_key(raw_api_key: str) -> str:
    pepper = get_settings().api_key_pepper.get_secret_value()
    return hmac.new(
        pepper.encode("utf-8"),
        raw_api_key.encode("utf-8"),
        sha256,
    ).hexdigest()


def api_key_digest_matches(raw_api_key: str, stored_digest: str) -> bool:
    candidate_digest = digest_api_key(raw_api_key)
    return hmac.compare_digest(candidate_digest, stored_digest)
