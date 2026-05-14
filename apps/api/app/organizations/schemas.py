from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationCreate(BaseModel):
    name: str


class OrganizationRead(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)
