from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.schemas.document import DocumentListResponse, DocumentTextRequest, DocumentTextResponse
from app.schemas.rag import AskRequest, AskResponse, HealthResponse
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


@router.post("/documents/text", response_model=DocumentTextResponse)
def ingest_text_document(
    request: DocumentTextRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> DocumentTextResponse:
    return rag_service.ingest_text(request)


@router.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> AskResponse:
    return rag_service.ask(request)
