from collections.abc import Generator
import importlib

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api_keys.models import ApiKey
from app.core.database import Base
from app.organizations.models import Organization
from app.projects.models import Project
from app.usage.service import ProjectQuotaExceededError, record_usage


@pytest.fixture()
def db() -> Generator[Session, None, None]:
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
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_record_usage_atomically_increments_project_usage_count(db: Session) -> None:
    organization = Organization(name="Acme")
    db.add(organization)
    db.flush()
    project = Project(organization_id=organization.id, name="Production", monthly_quota=1)
    db.add(project)
    db.flush()
    api_key = ApiKey(
        project_id=project.id,
        name="Server key",
        key_prefix="dm_testkey12",
        key_digest="digest",
    )
    db.add(api_key)
    db.commit()

    event = record_usage(
        db,
        api_key=api_key,
        endpoint="/v1/documents/process",
        units=2,
        llm_response={"summary": "ok"},
    )
    db.refresh(project)
    assert project.usage_count == 1
    assert event.llm_response == {"summary": "ok"}

    with pytest.raises(ProjectQuotaExceededError):
        record_usage(db, api_key=api_key, endpoint="/v1/documents/process", units=1)

    db.refresh(project)
    assert project.usage_count == 1
