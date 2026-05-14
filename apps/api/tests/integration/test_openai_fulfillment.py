import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from app.llm.schemas import DocumentAnalysis, LLMAnalysisRequest
from app.llm.service import OpenAILLMAnalyzer


@pytest.mark.anyio
@pytest.mark.integration
async def test_openai_fulfillment_live_document_analysis() -> None:
    env_local_path = Path(__file__).resolve().parents[2] / ".env.local"
    load_dotenv(env_local_path, override=True)

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or not api_key.startswith("sk-"):
        pytest.skip("OPENAI_API_KEY must be set in apps/api/.env.local for live integration")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    timeout_seconds = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "60"))

    analyzer = OpenAILLMAnalyzer(
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
    )
    assert analyzer.timeout_seconds == 60.0

    analysis = await analyzer.analyze_document(
        LLMAnalysisRequest(
            text="Invoice #1001 for $250 due May 30. Vendor: Acme Supplies.",
            filename="invoice.txt",
            source_mime_type="text/plain",
            character_count=58,
            metered_units=1,
        )
    )

    assert isinstance(analysis, DocumentAnalysis)
    assert analysis.summary
    assert analysis.document_type
    assert isinstance(analysis.key_points, list)
    assert isinstance(analysis.risk_flags, list)
