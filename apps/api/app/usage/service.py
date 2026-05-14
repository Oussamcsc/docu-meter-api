from sqlalchemy import func, update
from sqlalchemy.orm import Session

from app.api_keys.models import ApiKey
from app.projects.models import Project
from app.usage.models import UsageEvent


class ProjectQuotaExceededError(Exception):
    pass


def has_project_quota_remaining(db: Session, *, project_id: str) -> bool:
    project = db.get(Project, project_id)
    if project is None:
        return False
    return project.usage_count < project.monthly_quota


def increment_project_usage_count(db: Session, *, project_id: str) -> bool:
    result = db.execute(
        update(Project)
        .where(Project.id == project_id)
        .where(Project.usage_count < Project.monthly_quota)
        .values(usage_count=Project.usage_count + 1)
    )
    return result.rowcount == 1


def record_usage(
    db: Session,
    *,
    api_key: ApiKey,
    endpoint: str,
    units: int = 1,
    llm_response: dict | None = None,
) -> UsageEvent:
    did_increment = increment_project_usage_count(db, project_id=api_key.project_id)
    if not did_increment:
        db.rollback()
        raise ProjectQuotaExceededError("Project monthly quota exceeded")

    event = UsageEvent(
        project_id=api_key.project_id,
        api_key_id=api_key.id,
        endpoint=endpoint,
        units=units,
        llm_response=llm_response,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_project_usage_summary(db: Session, *, project_id: str) -> tuple[int, int]:
    events, units = (
        db.query(func.count(UsageEvent.id), func.coalesce(func.sum(UsageEvent.units), 0))
        .filter(UsageEvent.project_id == project_id)
        .one()
    )
    return int(events), int(units)
