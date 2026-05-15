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
from app.usage.routes import next_month_reset_date


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
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


def create_project(client: TestClient, *, monthly_quota: int = 100) -> str:
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
    return project_response.json()["id"]


def test_admin_usage_requires_admin_token(client: TestClient) -> None:
    project_id = create_project(client)

    response = client.get(f"/v1/usage?project_id={project_id}")

    assert response.status_code in {401, 503}
    assert response.json()["detail"] in {
        "Invalid admin token",
        "Admin API token is not configured",
    }


def test_admin_usage_returns_dashboard_summary(client: TestClient) -> None:
    fastapi_app.dependency_overrides[require_admin_token] = lambda: None
    project_id = create_project(client, monthly_quota=100)

    db_generator = fastapi_app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        from app.projects.models import Project

        project = db.get(Project, project_id)
        assert project is not None
        project.usage_count = 45
        db.commit()
    finally:
        db_generator.close()

    response = client.get(f"/v1/usage?project_id={project_id}")

    assert response.status_code == 200
    assert response.json() == {
        "project_id": project_id,
        "usage_count": 45,
        "monthly_quota": 100,
        "percentage": 45.0,
        "reset_date": next_month_reset_date().isoformat(),
    }


def test_admin_usage_returns_404_for_unknown_project(client: TestClient) -> None:
    fastapi_app.dependency_overrides[require_admin_token] = lambda: None

    response = client.get("/v1/usage?project_id=00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}
