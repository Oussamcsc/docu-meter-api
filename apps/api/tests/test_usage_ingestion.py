from collections.abc import Generator
import importlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.dependencies import require_admin_token
from app.core.database import Base, get_db
from app.core.redis import get_redis
from app.llm.schemas import DocumentAnalysis, LLMAnalysisRequest
from app.llm.service import AbstractBaseLLM, get_llm_analyzer
from app.main import app as fastapi_app


class FakeLLM(AbstractBaseLLM):
    async def analyze_document(self, request: LLMAnalysisRequest) -> DocumentAnalysis:
        return DocumentAnalysis(
            summary=request.text[:160],
            document_type=request.source_mime_type or "text",
            key_points=[request.text[:160]],
            risk_flags=[],
        )


class FakeRedis:
    async def eval(self, _script: str, _numkeys: int, _key: str, _ttl_seconds: int) -> int:
        return 1


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    importlib.import_module("app.api_keys.models")
    importlib.import_module("app.organizations.models")
    importlib.import_module("app.projects.models")
    importlib.import_module("app.usage.models")
    importlib.import_module("app.users.models")

    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def override_get_redis() -> Generator[FakeRedis, None, None]:
        yield FakeRedis()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    fastapi_app.dependency_overrides[get_redis] = override_get_redis
    fastapi_app.dependency_overrides[get_llm_analyzer] = lambda: FakeLLM()
    fastapi_app.dependency_overrides[require_admin_token] = lambda: None
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


def create_project_and_token(client: TestClient, *, monthly_quota: int = 100) -> tuple[str, str]:
    org_response = client.post("/organizations", json={"name": "Acme"})
    assert org_response.status_code == 201
    project_response = client.post(
        "/projects",
        json={
            "organization_id": org_response.json()["id"],
            "name": "Production",
            "monthly_quota": monthly_quota,
        },
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]
    key_response = client.post(
        f"/v1/projects/{project_id}/keys",
        json={"name": "Document processing token"},
    )
    assert key_response.status_code == 201
    return project_id, key_response.json()["key"]


def test_bearer_document_processing_increments_project_usage(client: TestClient) -> None:
    project_id, token = create_project_and_token(client)

    response = client.post(
        "/v1/documents/process",
        headers={"Authorization": f"Bearer {token}"},
        json={"filename": "doc.txt", "content": "invoice due tomorrow"},
    )

    assert response.status_code == 200
    assert response.json()["project_id"] == project_id
    assert response.json()["metered_units"] == 1

    telemetry = client.get(f"/v1/usage?project_id={project_id}")
    assert telemetry.status_code == 200
    assert telemetry.json()["usage_count"] == 1
    assert telemetry.json()["percentage"] == 1.0


def test_revoked_token_cannot_process_documents(client: TestClient) -> None:
    project_id, token = create_project_and_token(client)
    keys_response = client.get(f"/v1/keys?project_id={project_id}")
    api_key_id = keys_response.json()["keys"][0]["id"]

    revoke_response = client.delete(f"/v1/projects/{project_id}/keys/{api_key_id}")
    assert revoke_response.status_code == 200
    assert revoke_response.json()["is_active"] is False

    response = client.post(
        "/v1/documents/process",
        headers={"Authorization": f"Bearer {token}"},
        json={"filename": "doc.txt", "content": "invoice due tomorrow"},
    )

    assert response.status_code == 401
