import pytest

from app.documents.service import DocumentInput, DocumentService, DocumentTooLargeError, EmptyDocumentError
from app.llm.schemas import DocumentAnalysis, LLMAnalysisRequest
from app.llm.service import AbstractBaseLLM, LLMProviderError


class FakeLLM(AbstractBaseLLM):
    async def analyze_document(self, request: LLMAnalysisRequest) -> DocumentAnalysis:
        return DocumentAnalysis(
            summary=request.text,
            document_type=request.source_mime_type or "text",
            key_points=[],
            risk_flags=[],
        )


class FailingLLM(AbstractBaseLLM):
    async def analyze_document(self, request: LLMAnalysisRequest) -> DocumentAnalysis:
        raise LLMProviderError("provider down")


@pytest.mark.anyio
async def test_document_service_rejects_empty_extraction_results() -> None:
    service = DocumentService(llm=FakeLLM(), max_character_limit=5)

    with pytest.raises(EmptyDocumentError):
        await service.process(DocumentInput(filename="empty.txt", content=b"   "))


@pytest.mark.anyio
async def test_document_service_rejects_documents_over_character_limit() -> None:
    service = DocumentService(llm=FakeLLM(), max_character_limit=5)

    with pytest.raises(DocumentTooLargeError):
        await service.process(DocumentInput(filename="large.txt", content=b"123456"))


@pytest.mark.anyio
async def test_document_service_propagates_llm_provider_failure() -> None:
    service = DocumentService(llm=FailingLLM(), max_character_limit=100)

    with pytest.raises(LLMProviderError):
        await service.process(DocumentInput(filename="ok.txt", content=b"hello"))
