from uuid import UUID

from pydantic import BaseModel, Field


class SyncUserRequest(BaseModel):
    clerk_id: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=320)
    name: str | None = Field(default=None, max_length=200)


class SyncUserResponse(BaseModel):
    user_id: UUID
    clerk_id: str
    organization_id: UUID
    current_project_id: UUID
    created: bool
