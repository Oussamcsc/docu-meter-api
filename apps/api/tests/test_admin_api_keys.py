from collections.abc import Generator
import importlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api_keys.models import ApiKey
from app.auth.dependencies import require_admin_token
from app.core.database import Base, get_db
from app.core.security import api_key_digest_matches
from app.main import app as fastapi_app


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

    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    fastapi_app.dependency_overrides[require_admin_token] = lambda: None
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


def test_admin_can_create_api_key_once_visible_secret(client: TestClient) -> None:
    org_response = client.post("/organizations", json={"name": "Acme"})
    assert org_response.status_code == 201
    project_response = client.post(
        "/projects",
        json={
            "organization_id": org_response.json()["id"],
            "name": "Production",
            "monthly_quota": 1000,
        },
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    key_response = client.post(
        "/v1/keys",
        json={"project_id": project_id, "name": "Dashboard generated key"},
    )

    assert key_response.status_code == 201
    body = key_response.json()
    assert body["project_id"] == project_id
    assert body["name"] == "Dashboard generated key"
    assert body["key"].startswith("dm_live_")
    assert body["key_prefix"] == body["key"][:12]


def test_admin_can_list_api_keys_without_returning_secrets(client: TestClient) -> None:
    org_response = client.post("/organizations", json={"name": "Acme"})
    project_response = client.post(
        "/projects",
        json={"organization_id": org_response.json()["id"], "name": "Production"},
    )
    project_id = project_response.json()["id"]

    key_response = client.post(
        "/v1/keys",
        json={"project_id": project_id, "name": "Server key"},
    )
    assert key_response.status_code == 201

    list_response = client.get(f"/v1/keys?project_id={project_id}")

    assert list_response.status_code == 200
    body = list_response.json()
    assert body["project_id"] == project_id
    assert len(body["keys"]) == 1
    listed_key = body["keys"][0]
    assert listed_key["name"] == "Server key"
    assert listed_key["key_prefix"] == key_response.json()["key_prefix"]
    assert listed_key["masked_token"] == f"{key_response.json()['key_prefix']}_••••••••"
    assert "key" not in listed_key
    assert "api_key" not in listed_key
    assert "key_digest" not in listed_key


def test_admin_api_key_creation_stores_only_peppered_digest(client: TestClient) -> None:
    org_response = client.post("/organizations", json={"name": "Acme"})
    project_response = client.post(
        "/projects",
        json={"organization_id": org_response.json()["id"], "name": "Production"},
    )
    project_id = project_response.json()["id"]

    key_response = client.post(
        "/v1/keys",
        json={"project_id": project_id, "name": "Server key"},
    )
    assert key_response.status_code == 201
    raw_key = key_response.json()["key"]

    db_generator = fastapi_app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        stored_key = db.query(ApiKey).filter(ApiKey.project_id == project_id).one()
        assert stored_key.key_digest != raw_key
        assert raw_key not in stored_key.key_digest
        assert api_key_digest_matches(raw_key, stored_key.key_digest)
    finally:
        db_generator.close()
