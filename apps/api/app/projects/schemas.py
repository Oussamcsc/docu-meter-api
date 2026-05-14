from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    organization_id: UUID
    name: str
    monthly_quota: int = Field(default=1000, ge=1)


class ProjectRead(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    monthly_quota: int
    usage_count: int

    model_config = ConfigDict(from_attributes=True)
