import json
from abc import ABC, abstractmethod

from openai import AsyncOpenAI, OpenAIError

from app.core.config import get_settings
from app.llm.prompts import DOCUMENT_ANALYSIS_SYSTEM_PROMPT
from app.llm.schemas import DocumentAnalysis, LLMAnalysisRequest


class LLMProviderError(RuntimeError):
    pass


class AbstractBaseLLM(ABC):
    """Provider-agnostic interface for document analysis models."""

    @abstractmethod
    async def analyze_document(self, request: LLMAnalysisRequest) -> DocumentAnalysis:
        """Analyze extracted document text and return normalized product output."""


class MockLLMAnalyzer(AbstractBaseLLM):
    """Deterministic analyzer used until the real LLM provider is wired."""

    async def analyze_document(self, request: LLMAnalysisRequest) -> DocumentAnalysis:
        normalized = " ".join(request.text.split())
        preview = normalized[:160] if normalized else "No extracted text."
        lowered = normalized.lower()
        risk_flags: list[str] = []
        if "due" in lowered or "invoice" in lowered:
            risk_flags.append("payment_related")
        if "confidential" in lowered:
            risk_flags.append("confidential_content")

        return DocumentAnalysis(
            summary=preview,
            document_type=request.source_mime_type or "text",
            key_points=[preview] if preview else [],
            risk_flags=risk_flags,
        )


class OpenAILLMAnalyzer(AbstractBaseLLM):
    def __init__(self, *, api_key: str, model: str, timeout_seconds: float) -> None:
        self.client = AsyncOpenAI(api_key=api_key, timeout=timeout_seconds)
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def analyze_document(self, request: LLMAnalysisRequest) -> DocumentAnalysis:
        user_prompt = (
            f"Filename: {request.filename}\n"
            f"Source MIME type: {request.source_mime_type}\n"
            f"Character count: {request.character_count}\n"
            f"Metered units: {request.metered_units}\n\n"
            f"Document text:\n{request.text}"
        )
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": DOCUMENT_ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
        except OpenAIError as exc:
            raise LLMProviderError("OpenAI document analysis failed") from exc

        content = response.choices[0].message.content
        if not content:
            raise LLMProviderError("OpenAI returned an empty analysis response")

        try:
            payload = json.loads(content)
            return DocumentAnalysis.model_validate(payload)
        except (json.JSONDecodeError, ValueError) as exc:
            raise LLMProviderError("OpenAI returned an invalid analysis payload") from exc


def get_llm_analyzer() -> AbstractBaseLLM:
    settings = get_settings()
    return OpenAILLMAnalyzer(
        api_key=settings.openai_api_key.get_secret_value(),
        model=settings.openai_model,
        timeout_seconds=settings.openai_timeout_seconds,
    )
