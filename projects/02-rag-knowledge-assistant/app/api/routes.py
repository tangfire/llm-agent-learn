from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request

from app.schemas.document import (
    DocumentFilePathRequest,
    DocumentListResponse,
    DocumentTextRequest,
    DocumentTextResponse,
)
from app.schemas.rag import (
    AskRequest,
    AskResponse,
    HealthResponse,
    QueryTraceListResponse,
)
from app.services.rag import RAGService

router = APIRouter()


def get_rag_service(request: Request) -> RAGService:
    return request.app.state.rag_service


@router.get("/health", response_model=HealthResponse)
def health(rag_service: RAGService = Depends(get_rag_service)) -> HealthResponse:
    return rag_service.health()


@router.get("/documents", response_model=DocumentListResponse)
def list_documents(
    rag_service: RAGService = Depends(get_rag_service),
) -> DocumentListResponse:
    return rag_service.list_documents()


@router.get("/traces", response_model=QueryTraceListResponse)
def list_query_traces(
    limit: int = Query(default=20, ge=1, le=100),
    rag_service: RAGService = Depends(get_rag_service),
) -> QueryTraceListResponse:
    return rag_service.list_query_traces(limit=limit)


@router.post("/documents/text", response_model=DocumentTextResponse)
def ingest_text_document(
    request: DocumentTextRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> DocumentTextResponse:
    return rag_service.ingest_text(request)


@router.post("/documents/file-path", response_model=DocumentTextResponse)
def ingest_file_path_document(
    request: DocumentFilePathRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> DocumentTextResponse:
    return rag_service.ingest_file_path(request)


@router.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> AskResponse:
    return rag_service.ask(request)
