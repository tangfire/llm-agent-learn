from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models


@dataclass(frozen=True)
class StoredChunk:
    chunk_id: str
    document_id: str
    title: str
    source: str | None
    tags: list[str]
    chunk_index: int
    text: str
    char_count: int


@dataclass(frozen=True)
class ScoredChunk:
    chunk: StoredChunk
    score: float


class QdrantVectorStore:
    def __init__(self, storage_path: str, collection_name: str, vector_size: int) -> None:
        Path(storage_path).mkdir(parents=True, exist_ok=True)
        self.storage_path = storage_path
        self.collection_name = collection_name
        self.vector_size = vector_size
        self._client = QdrantClient(path=storage_path)
        self._ensure_collection()

    def upsert_chunks(
        self, chunks: list[StoredChunk], embeddings: list[list[float]]
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("The number of chunks and embeddings must match.")

        points = [
            models.PointStruct(
                id=self._point_id(chunk.chunk_id),
                vector=embedding,
                payload=self._payload_from_chunk(chunk),
            )
            for chunk, embedding in zip(chunks, embeddings, strict=True)
        ]
        self._client.upsert(collection_name=self.collection_name, points=points)

    def retrieve(self, query_vector: list[float], limit: int) -> list[ScoredChunk]:
        response = self._client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        return [
            ScoredChunk(
                chunk=self._chunk_from_payload(point.payload or {}),
                score=float(point.score),
            )
            for point in response.points
        ]

    def describe(self) -> str:
        return f"qdrant-local:{self.collection_name}:{self.vector_size}d"

    def count_chunks(self) -> int:
        result = self._client.count(collection_name=self.collection_name, exact=True)
        return int(result.count)

    def close(self) -> None:
        self._client.close()

    def _ensure_collection(self) -> None:
        if not self._client.collection_exists(self.collection_name):
            self._client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE,
                ),
            )
            return

        collection_info = self._client.get_collection(self.collection_name)
        actual_vector_size = collection_info.config.params.vectors.size
        if actual_vector_size != self.vector_size:
            raise RuntimeError(
                "Qdrant collection vector size does not match the current embedding "
                f"dimension. collection={actual_vector_size}, expected={self.vector_size}"
            )

    def _payload_from_chunk(self, chunk: StoredChunk) -> dict[str, object]:
        return {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "title": chunk.title,
            "source": chunk.source,
            "tags": chunk.tags,
            "chunk_index": chunk.chunk_index,
            "text": chunk.text,
            "char_count": chunk.char_count,
        }

    def _point_id(self, chunk_id: str) -> uuid.UUID:
        return uuid.uuid5(uuid.NAMESPACE_URL, chunk_id)

    def _chunk_from_payload(self, payload: dict[str, object]) -> StoredChunk:
        text = str(payload.get("text", ""))
        raw_tags = payload.get("tags", [])
        tags = [str(item) for item in raw_tags] if isinstance(raw_tags, list) else []
        return StoredChunk(
            chunk_id=str(payload.get("chunk_id", "")),
            document_id=str(payload.get("document_id", "")),
            title=str(payload.get("title", "")),
            source=payload.get("source") if payload.get("source") else None,
            tags=tags,
            chunk_index=int(payload.get("chunk_index", 0)),
            text=text,
            char_count=int(payload.get("char_count", len(text))),
        )
