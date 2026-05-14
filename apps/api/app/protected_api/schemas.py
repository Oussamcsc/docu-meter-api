from pydantic import BaseModel, Field

from app.llm.schemas import DocumentAnalysis


class DocumentProcessRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class DocumentProcessResponse(BaseModel):
    project_id: str
    filename: str
    characters: int
    metered_units: int
    analysis: DocumentAnalysis
    status: str = "processed"
