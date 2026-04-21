from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.schemas.document import ChunkConfig


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

    @field_validator("question")
    @classmethod
    def validate_non_blank_question(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("must not be blank")
        return normalized


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    mode: str


class HealthResponse(BaseModel):
    status: str
    chat_model: str
    chat_mode: str
    embedding_model: str
    embedding_mode: str
    vector_store: str
    retrieval_mode: str
    stored_chunks: int
    chunk_config: ChunkConfig
