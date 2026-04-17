from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.document import DocumentTextRequest, DocumentTextResponse
from app.schemas.rag import AskRequest, AskResponse, HealthResponse
from app.services.rag import RAGService

router = APIRouter()
rag_service = RAGService(settings)


def close_services() -> None:
    rag_service.close()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return rag_service.health()


@router.post("/documents/text", response_model=DocumentTextResponse)
def ingest_text_document(request: DocumentTextRequest) -> DocumentTextResponse:
    try:
        return rag_service.ingest_text(request)
    except Exception as exc:  # pragma: no cover - starter scaffold
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        return rag_service.ask(request)
    except Exception as exc:  # pragma: no cover - starter scaffold
        raise HTTPException(status_code=502, detail=str(exc)) from exc
