from dataclasses import dataclass
from pathlib import Path

from app.core.config import get_settings
from app.documents.extractors import ExtractedDocument, extract_pdf_text, extract_txt_text
from app.llm.schemas import DocumentAnalysis, LLMAnalysisRequest
from app.llm.service import AbstractBaseLLM


class UnsupportedDocumentTypeError(ValueError):
    pass


class DocumentTooLargeError(ValueError):
    pass


class EmptyDocumentError(ValueError):
    pass


@dataclass(frozen=True)
class DocumentInput:
    filename: str
    content: bytes

    @property
    def extension(self) -> str:
        return Path(self.filename).suffix.lower()


@dataclass(frozen=True)
class ProcessedDocument:
    characters: int
    metered_units: int
    analysis: DocumentAnalysis


class DocumentService:
    def __init__(self, *, llm: AbstractBaseLLM, max_character_limit: int | None = None) -> None:
        self.llm = llm
        self.max_character_limit = max_character_limit or get_settings().max_document_characters

    async def extract_text(self, document: DocumentInput) -> ExtractedDocument:
        if document.extension == ".txt":
            return extract_txt_text(document.content)
        if document.extension == ".pdf":
            return extract_pdf_text(document.content)
        raise UnsupportedDocumentTypeError(f"Unsupported document type: {document.extension}")

    def enforce_character_floor(self, *, character_count: int) -> None:
        if character_count < 1:
            raise EmptyDocumentError("Document extraction produced no text")

    def enforce_size_limit(self, *, character_count: int) -> None:
        if character_count > self.max_character_limit:
            raise DocumentTooLargeError(
                f"Document has {character_count} characters; limit is {self.max_character_limit}"
            )

    def calculate_metered_units(self, *, character_count: int) -> int:
        # MVP formula: 1 unit per 1,000 extracted characters, minimum 1 unit.
        return max(1, (character_count + 999) // 1000)

    async def process(self, document: DocumentInput) -> ProcessedDocument:
        extracted = await self.extract_text(document)
        self.enforce_character_floor(character_count=extracted.characters)
        self.enforce_size_limit(character_count=extracted.characters)
        metered_units = self.calculate_metered_units(character_count=extracted.characters)
        analysis = await self.llm.analyze_document(
            LLMAnalysisRequest(
                text=extracted.text,
                filename=document.filename,
                source_mime_type=extracted.mime_type,
                character_count=extracted.characters,
                metered_units=metered_units,
            )
        )
        return ProcessedDocument(
            characters=extracted.characters,
            metered_units=metered_units,
            analysis=analysis,
        )
