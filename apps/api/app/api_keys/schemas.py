from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ApiKeyCreate(BaseModel):
    project_id: UUID
    name: str


class ApiKeyCreateForProject(BaseModel):
    name: str


class ApiKeyCreated(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    key_prefix: str
    api_key: str


class AdminApiKeyCreated(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    key_prefix: str
    key: str


class ApiKeyRead(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    key_prefix: str
    is_active: bool
    masked_token: str

    model_config = ConfigDict(from_attributes=True)


class AdminApiKeyList(BaseModel):
    project_id: UUID
    keys: list[ApiKeyRead]
