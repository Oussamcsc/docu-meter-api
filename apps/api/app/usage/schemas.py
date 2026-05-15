from datetime import date
from uuid import UUID

from pydantic import BaseModel


class UsageSummary(BaseModel):
    project_id: UUID
    events: int
    units: int


class AdminUsageSummary(BaseModel):
    project_id: UUID
    usage_count: int
    monthly_quota: int
    percentage: float
    reset_date: date
