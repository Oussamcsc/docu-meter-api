from uuid import UUID

from pydantic import BaseModel


class UsageSummary(BaseModel):
    project_id: UUID
    events: int
    units: int
