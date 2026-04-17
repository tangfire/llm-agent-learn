from __future__ import annotations

from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: str
    title: str
    source: str | None = None
    chunk_id: str
    chunk_index: int


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    source: str | None = None
    chunk_index: int
    text: str
    score: float


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    top_k: int = Field(default=3, ge=1, le=10, description="返回的检索片段数量")


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    mode: str


class HealthResponse(BaseModel):
    status: str
    chat_model: str
    embedding_model: str
    vector_store: str
    retrieval_mode: str
