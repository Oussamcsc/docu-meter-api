from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api_keys.models import ApiKey
from app.core.database import get_db
from app.documents.service import DocumentInput, DocumentService, DocumentTooLargeError, EmptyDocumentError
from app.llm.service import AbstractBaseLLM, LLMProviderError, get_llm_analyzer
from app.protected_api.dependencies import require_api_key
from app.protected_api.schemas import DocumentProcessRequest, DocumentProcessResponse
from app.quotas.service import enforce_project_quota
from app.rate_limits.dependencies import enforce_project_rate_limit
from app.rate_limits.service import RateLimitResult
from app.usage.service import record_usage

router = APIRouter(prefix="/v1", tags=["protected-api"])


@router.post("/documents/process", response_model=DocumentProcessResponse)
async def process_document(
    payload: DocumentProcessRequest,
    api_key: ApiKey = Depends(require_api_key),
    _rate_limit: RateLimitResult = Depends(enforce_project_rate_limit),
    _quota: None = Depends(enforce_project_quota),
    analyzer: AbstractBaseLLM = Depends(get_llm_analyzer),
    db: Session = Depends(get_db),
) -> DocumentProcessResponse:
    document_service = DocumentService(llm=analyzer)
    try:
        processed = await document_service.process(
            DocumentInput(filename=payload.filename, content=payload.content.encode("utf-8"))
        )
    except EmptyDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except DocumentTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc
    except LLMProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Document analysis provider failed",
        ) from exc

    # Meter only after extraction, guard checks, unit calculation, and LLM analysis succeed.
    record_usage(
        db,
        api_key=api_key,
        endpoint="/v1/documents/process",
        units=processed.metered_units,
        llm_response=processed.analysis.model_dump(),
    )
    return DocumentProcessResponse(
        project_id=api_key.project_id,
        filename=payload.filename,
        characters=processed.characters,
        metered_units=processed.metered_units,
        analysis=processed.analysis,
    )
