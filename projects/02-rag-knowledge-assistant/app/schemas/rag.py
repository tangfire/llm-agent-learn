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


class RetrievalConfig(BaseModel):
    low_confidence_score_threshold: float
    rerank_enabled: bool


class RetrievalDebug(BaseModel):
    requested_top_k: int
    candidate_limit: int
    rerank_applied: bool
    low_confidence_score_threshold: float
    retrieved_count: int
    best_score: float | None = None
    decision: str
    rejection_reason: str | None = None


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    top_k: int = Field(default=3, ge=1, le=10, description="返回的检索片段数量")
    return_debug: bool = Field(default=False, description="是否返回检索调试信息")

    @field_validator("question")
    @classmethod
    def validate_non_blank_question(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("must not be blank")
        return normalized


class AskResponse(BaseModel):
    status: str
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    mode: str
    debug: RetrievalDebug | None = None


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
    retrieval_config: RetrievalConfig
