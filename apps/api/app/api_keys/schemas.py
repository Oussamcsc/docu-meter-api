from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ApiKeyCreate(BaseModel):
    project_id: UUID
    name: str


class ApiKeyCreated(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    key_prefix: str
    api_key: str


class ApiKeyRead(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    key_prefix: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
