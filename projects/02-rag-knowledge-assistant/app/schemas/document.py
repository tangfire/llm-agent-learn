from __future__ import annotations

from pydantic import BaseModel, Field


class ChunkPreview(BaseModel):
    chunk_id: str
    chunk_index: int
    text: str
    char_count: int


class DocumentTextRequest(BaseModel):
    title: str = Field(..., min_length=1, description="文档标题")
    text: str = Field(..., min_length=1, description="文档原文")
    source: str | None = Field(default=None, description="来源文件名或来源标识")
    tags: list[str] = Field(default_factory=list, description="可选标签")


class DocumentTextResponse(BaseModel):
    document_id: str
    status: str
    title: str
    source: str | None = None
    chunk_count: int
    chunk_preview: list[ChunkPreview] = Field(default_factory=list)
