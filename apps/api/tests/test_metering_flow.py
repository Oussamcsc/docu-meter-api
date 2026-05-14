from collections.abc import Generator
import importlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.redis import get_redis
from app.llm.schemas import DocumentAnalysis, LLMAnalysisRequest
from app.llm.service import AbstractBaseLLM, get_llm_analyzer
from app.main import app as fastapi_app


class FakeLLM(AbstractBaseLLM):
    async def analyze_document(self, request: LLMAnalysisRequest) -> DocumentAnalysis:
        lowered = request.text.lower()
        risk_flags = ["payment_related"] if "invoice" in lowered or "due" in lowered else []
        return DocumentAnalysis(
            summary=request.text[:160],
            document_type=request.source_mime_type or "text",
            key_points=[request.text[:160]],
            risk_flags=risk_flags,
        )


class FakeRedis:
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}
        self.expirations: dict[str, int] = {}

    async def eval(self, _script: str, _numkeys: int, key: str, ttl_seconds: int) -> int:
        self.counts[key] = self.counts.get(key, 0) + 1
        if self.counts[key] == 1:
            self.expirations[key] = ttl_seconds
        return self.counts[key]


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Import models before create_all.
    importlib.import_module("app.api_keys.models")
    importlib.import_module("app.organizations.models")
    importlib.import_module("app.projects.models")
    importlib.import_module("app.usage.models")

    Base.metadata.create_all(bind=engine)
    fake_redis = FakeRedis()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def override_get_redis() -> Generator[FakeRedis, None, None]:
        yield fake_redis

    fastapi_app.dependency_overrides[get_db] = override_get_db
    fastapi_app.dependency_overrides[get_redis] = override_get_redis
    fastapi_app.dependency_overrides[get_llm_analyzer] = lambda: FakeLLM()
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


def test_api_key_metering_flow(client: TestClient) -> None:
    org_response = client.post("/organizations", json={"name": "Acme"})
    assert org_response.status_code == 201
    org_id = org_response.json()["id"]

    project_response = client.post(
        "/projects",
        json={"organization_id": org_id, "name": "Production", "monthly_quota": 1},
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    key_response = client.post(
        "/api-keys",
        json={"project_id": project_id, "name": "Server key"},
    )
    assert key_response.status_code == 201
    api_key = key_response.json()["api_key"]
    assert api_key.startswith("dm_")

    missing_key_response = client.post(
        "/v1/documents/process",
        json={"filename": "invoice.txt", "content": "hello"},
    )
    assert missing_key_response.status_code == 401

    x_api_key_response = client.post(
        "/v1/documents/process",
        headers={"X-API-Key": api_key},
        json={"filename": "invoice.txt", "content": "hello"},
    )
    assert x_api_key_response.status_code == 401

    process_response = client.post(
        "/v1/documents/process",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"filename": "invoice.txt", "content": "invoice due " + ("x" * 1200)},
    )
    assert process_response.status_code == 200
    assert process_response.headers["X-RateLimit-Limit"] == "60"
    assert process_response.headers["X-RateLimit-Remaining"] == "59"
    assert "X-RateLimit-Reset" in process_response.headers
    processed = process_response.json()
    assert processed["metered_units"] == 2
    assert processed["analysis"]["document_type"] == "text/plain"
    assert "payment_related" in processed["analysis"]["risk_flags"]

    quota_response = client.post(
        "/v1/documents/process",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"filename": "second.txt", "content": "second document"},
    )
    assert quota_response.status_code == 403

    usage_response = client.get(f"/usage/projects/{project_id}")
    assert usage_response.status_code == 200
    assert usage_response.json() == {"project_id": project_id, "events": 1, "units": 2}
