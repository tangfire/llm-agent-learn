from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.schemas.document import ChunkConfig


def _normalize_string_list(values: list[str]) -> list[str]:
    seen: set[str] = set()
    normalized_values: list[str] = []
    for value in values:
        item = value.strip()
        if not item or item in seen:
            continue
        seen.add(item)
        normalized_values.append(item)
    return normalized_values


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
    filtered_document_ids: list[str] = Field(default_factory=list)
    filtered_tags: list[str] = Field(default_factory=list)
    best_score: float | None = None
    decision: str
    rejection_reason: str | None = None
    trace_id: str | None = None


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    top_k: int = Field(default=3, ge=1, le=10, description="返回的检索片段数量")
    document_ids: list[str] = Field(
        default_factory=list,
        description="可选文档范围过滤，只在这些 document_id 里检索",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="可选标签过滤，只在匹配标签的文档里检索",
    )
    return_debug: bool = Field(default=False, description="是否返回检索调试信息")

    @field_validator("question")
    @classmethod
    def validate_non_blank_question(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("must not be blank")
        return normalized

    @field_validator("document_ids", "tags")
    @classmethod
    def normalize_filters(cls, values: list[str]) -> list[str]:
        return _normalize_string_list(values)


class AskResponse(BaseModel):
    status: str
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    mode: str
    debug: RetrievalDebug | None = None


class QueryTraceSummary(BaseModel):
    trace_id: str
    created_at: str
    question: str
    status: str
    mode: str
    requested_top_k: int
    candidate_limit: int
    filtered_document_ids: list[str] = Field(default_factory=list)
    filtered_tags: list[str] = Field(default_factory=list)
    retrieved_count: int
    best_score: float | None = None
    rejection_reason: str | None = None
    citations: list[Citation] = Field(default_factory=list)


class QueryTraceListResponse(BaseModel):
    total: int
    traces: list[QueryTraceSummary] = Field(default_factory=list)


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
