from collections.abc import Generator
import importlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.dependencies import require_admin_token
from app.core.database import Base, get_db
from app.main import app as fastapi_app
from app.organizations.models import Organization
from app.projects.models import Project
from app.users.models import OrganizationMembership, User


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

    fastapi_app.dependency_overrides[get_db] = override_get_db
    fastapi_app.dependency_overrides[require_admin_token] = lambda: None
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


def test_sync_user_provisions_default_workspace(client: TestClient) -> None:
    response = client.post(
        "/v1/internal/sync-user",
        json={
            "clerk_id": "user_123",
            "email": "oussama@example.com",
            "name": "Oussama",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["clerk_id"] == "user_123"
    assert body["created"] is True
    assert body["organization_id"]
    assert body["current_project_id"]

    db_generator = fastapi_app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        user = db.query(User).filter(User.clerk_id == "user_123").one()
        organization = db.get(Organization, body["organization_id"])
        project = db.get(Project, body["current_project_id"])
        membership = db.query(OrganizationMembership).filter_by(user_id=user.id).one()

        assert user.email == "oussama@example.com"
        assert user.current_org_id == body["organization_id"]
        assert user.current_project_id == body["current_project_id"]
        assert organization is not None
        assert organization.name == "Oussama's Org"
        assert project is not None
        assert project.organization_id == organization.id
        assert project.name == "Default Project"
        assert membership.organization_id == organization.id
        assert membership.role == "owner"
    finally:
        db_generator.close()


def test_sync_user_is_idempotent_and_returns_existing_project(client: TestClient) -> None:
    payload = {
        "clerk_id": "user_existing",
        "email": "existing@example.com",
        "name": "Existing",
    }

    first = client.post("/v1/internal/sync-user", json=payload)
    second = client.post("/v1/internal/sync-user", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    first_body = first.json()
    second_body = second.json()
    assert first_body["created"] is True
    assert second_body["created"] is False
    assert second_body["user_id"] == first_body["user_id"]
    assert second_body["organization_id"] == first_body["organization_id"]
    assert second_body["current_project_id"] == first_body["current_project_id"]

    db_generator = fastapi_app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        assert db.query(User).count() == 1
        assert db.query(Organization).count() == 1
        assert db.query(Project).count() == 1
        assert db.query(OrganizationMembership).count() == 1
    finally:
        db_generator.close()
