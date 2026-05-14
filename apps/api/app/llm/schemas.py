from pydantic import BaseModel, Field


class LLMAnalysisRequest(BaseModel):
    text: str = Field(min_length=1)
    filename: str
    source_mime_type: str | None = None
    character_count: int
    metered_units: int


class DocumentAnalysis(BaseModel):
    summary: str
    document_type: str
    key_points: list[str]
    risk_flags: list[str]
