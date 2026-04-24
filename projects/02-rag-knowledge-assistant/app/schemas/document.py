from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class IngestStrategy(StrEnum):
    KEEP_BOTH = "keep_both"
    REJECT_DUPLICATE = "reject_duplicate"
    REPLACE_EXISTING = "replace_existing"


class ChunkConfig(BaseModel):
    chunk_size: int
    chunk_overlap: int


class ChunkPreview(BaseModel):
    chunk_id: str
    chunk_index: int
    text: str
    char_count: int


class DocumentMetadata(BaseModel):
    document_id: str
    title: str
    source: str | None = None
    source_type: str
    tags: list[str] = Field(default_factory=list)
    chunk_count: int
    total_char_count: int
    ingested_at: str | None = None


class DocumentTextRequest(BaseModel):
    title: str = Field(..., min_length=1, description="文档标题")
    text: str = Field(..., min_length=1, description="文档原文")
    source: str | None = Field(default=None, description="来源文件名或来源标识")
    tags: list[str] = Field(default_factory=list, description="可选标签")
    ingest_strategy: IngestStrategy = Field(
        default=IngestStrategy.REPLACE_EXISTING,
        description="重复导入时的处理策略",
    )

    @field_validator("title", "text")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("must not be blank")
        return normalized

    @field_validator("source")
    @classmethod
    def normalize_source(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, values: list[str]) -> list[str]:
        seen: set[str] = set()
        normalized_tags: list[str] = []
        for value in values:
            tag = value.strip()
            if not tag or tag in seen:
                continue
            seen.add(tag)
            normalized_tags.append(tag)
        return normalized_tags


class DocumentFilePathRequest(BaseModel):
    path: str = Field(..., min_length=1, description="本地文件路径")
    title: str | None = Field(default=None, description="可选标题，默认取文件名")
    source: str | None = Field(default=None, description="可选来源标识，默认取文件路径")
    tags: list[str] = Field(default_factory=list, description="可选标签")
    ingest_strategy: IngestStrategy = Field(
        default=IngestStrategy.REPLACE_EXISTING,
        description="重复导入时的处理策略",
    )

    @field_validator("path")
    @classmethod
    def validate_non_blank_path(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("must not be blank")
        return normalized

    @field_validator("title", "source")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, values: list[str]) -> list[str]:
        seen: set[str] = set()
        normalized_tags: list[str] = []
        for value in values:
            tag = value.strip()
            if not tag or tag in seen:
                continue
            seen.add(tag)
            normalized_tags.append(tag)
        return normalized_tags


class DocumentTextResponse(BaseModel):
    document_id: str
    status: str
    title: str
    source: str | None = None
    source_type: str
    chunk_count: int
    chunk_preview: list[ChunkPreview] = Field(default_factory=list)
    chunk_config: ChunkConfig
    ingested_at: str
    dedupe_action: str
    ingest_strategy: IngestStrategy


class DocumentListResponse(BaseModel):
    total_documents: int
    chunk_config: ChunkConfig
    documents: list[DocumentMetadata] = Field(default_factory=list)
