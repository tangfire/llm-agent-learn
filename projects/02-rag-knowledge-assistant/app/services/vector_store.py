from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from qdrant_client import QdrantClient


@dataclass(frozen=True)
class StoredChunk:
    chunk_id: str
    document_id: str
    title: str
    source: str | None
    chunk_index: int
    text: str


@dataclass(frozen=True)
class StoredDocument:
    document_id: str
    title: str
    source: str | None
    tags: list[str]
    text: str
    chunks: list[StoredChunk]


@dataclass(frozen=True)
class ScoredChunk:
    chunk: StoredChunk
    score: float


class QdrantVectorStore:
    def __init__(self, storage_path: str, collection_name: str) -> None:
        Path(storage_path).mkdir(parents=True, exist_ok=True)
        self.storage_path = storage_path
        self.collection_name = collection_name
        self._client = QdrantClient(path=storage_path)
        self._documents: dict[str, StoredDocument] = {}

    def save_document(self, document: StoredDocument) -> None:
        self._documents[document.document_id] = document

    def retrieve(self, query: str, limit: int) -> list[ScoredChunk]:
        if not query.strip():
            return []

        scored_chunks: list[ScoredChunk] = []
        for document in self._documents.values():
            for chunk in document.chunks:
                score = self._score(query=query, text=chunk.text)
                if score > 0:
                    scored_chunks.append(ScoredChunk(chunk=chunk, score=score))

        scored_chunks.sort(key=lambda item: item.score, reverse=True)
        return scored_chunks[:limit]

    def describe(self) -> str:
        return f"qdrant-local:{self.collection_name}"

    def close(self) -> None:
        self._client.close()

    def _score(self, query: str, text: str) -> float:
        normalized_query = "".join(query.lower().split())
        normalized_text = text.lower()
        if not normalized_query:
            return 0

        overlap = sum(1 for char in set(normalized_query) if char in normalized_text)
        return overlap / max(len(set(normalized_query)), 1)
