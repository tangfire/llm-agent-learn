from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.core.errors import ServiceConfigurationError, StorageError

logger = logging.getLogger(__name__)


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
    ingested_at: str | None = None


@dataclass(frozen=True)
class ScoredChunk:
    chunk: StoredChunk
    score: float


@dataclass(frozen=True)
class DocumentSummary:
    document_id: str
    title: str
    source: str | None
    tags: list[str]
    chunk_count: int
    total_char_count: int
    ingested_at: str | None


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

        try:
            points = [
                models.PointStruct(
                    id=self._point_id(chunk.chunk_id),
                    vector=embedding,
                    payload=self._payload_from_chunk(chunk),
                )
                for chunk, embedding in zip(chunks, embeddings, strict=True)
            ]
            self._client.upsert(collection_name=self.collection_name, points=points)
        except Exception as exc:
            raise StorageError(
                "Failed to persist document chunks into qdrant.",
                error_code="vector_store_upsert_failed",
            ) from exc

    def retrieve(self, query_vector: list[float], limit: int) -> list[ScoredChunk]:
        try:
            response = self._client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
        except Exception as exc:
            raise StorageError(
                "Failed to retrieve chunks from qdrant.",
                error_code="vector_store_retrieve_failed",
            ) from exc

        return [
            ScoredChunk(
                chunk=self._chunk_from_payload(point.payload or {}),
                score=float(point.score),
            )
            for point in response.points
        ]

    def list_documents(self) -> list[DocumentSummary]:
        try:
            offset: int | str | uuid.UUID | models.PointId | None = None
            aggregated: dict[str, dict[str, object]] = {}

            while True:
                records, offset = self._client.scroll(
                    collection_name=self.collection_name,
                    limit=128,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False,
                )
                if not records:
                    break

                for record in records:
                    chunk = self._chunk_from_payload(record.payload or {})
                    if not chunk.document_id:
                        continue

                    current = aggregated.setdefault(
                        chunk.document_id,
                        {
                            "document_id": chunk.document_id,
                            "title": chunk.title,
                            "source": chunk.source,
                            "tags": set(chunk.tags),
                            "chunk_count": 0,
                            "total_char_count": 0,
                            "ingested_at": chunk.ingested_at,
                        },
                    )
                    current["chunk_count"] = int(current["chunk_count"]) + 1
                    current["total_char_count"] = (
                        int(current["total_char_count"]) + chunk.char_count
                    )
                    current_tags = current["tags"]
                    if isinstance(current_tags, set):
                        current_tags.update(chunk.tags)
                    if current["ingested_at"] is None and chunk.ingested_at is not None:
                        current["ingested_at"] = chunk.ingested_at

                if offset is None:
                    break
        except Exception as exc:
            raise StorageError(
                "Failed to list indexed documents from qdrant.",
                error_code="vector_store_list_failed",
            ) from exc

        documents = [
            DocumentSummary(
                document_id=str(item["document_id"]),
                title=str(item["title"]),
                source=item["source"] if item["source"] else None,
                tags=sorted(str(tag) for tag in item["tags"]),
                chunk_count=int(item["chunk_count"]),
                total_char_count=int(item["total_char_count"]),
                ingested_at=(
                    str(item["ingested_at"])
                    if item["ingested_at"] is not None
                    else None
                ),
            )
            for item in aggregated.values()
        ]
        documents.sort(key=lambda item: ((item.ingested_at or ""), item.title.lower()), reverse=True)
        return documents

    def describe(self) -> str:
        return f"qdrant-local:{self.collection_name}:{self.vector_size}d"

    def count_chunks(self) -> int:
        try:
            result = self._client.count(collection_name=self.collection_name, exact=True)
        except Exception as exc:
            raise StorageError(
                "Failed to count stored chunks in qdrant.",
                error_code="vector_store_count_failed",
            ) from exc
        return int(result.count)

    def close(self) -> None:
        self._client.close()

    def _ensure_collection(self) -> None:
        try:
            if not self._client.collection_exists(self.collection_name):
                self._client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE,
                    ),
                )
                logger.info(
                    "Created qdrant collection | collection=%s | vector_size=%s",
                    self.collection_name,
                    self.vector_size,
                )
                return

            collection_info = self._client.get_collection(self.collection_name)
            actual_vector_size = collection_info.config.params.vectors.size
        except Exception as exc:
            raise StorageError(
                "Failed to initialize qdrant collection.",
                error_code="vector_store_init_failed",
            ) from exc

        if actual_vector_size != self.vector_size:
            raise ServiceConfigurationError(
                "Qdrant collection vector size does not match current embedding dimension. "
                f"collection={actual_vector_size}, expected={self.vector_size}",
                error_code="qdrant_dimension_mismatch",
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
            "ingested_at": chunk.ingested_at,
        }

    def _point_id(self, chunk_id: str) -> uuid.UUID:
        return uuid.uuid5(uuid.NAMESPACE_URL, chunk_id)

    def _chunk_from_payload(self, payload: dict[str, object]) -> StoredChunk:
        text = str(payload.get("text", ""))
        raw_tags = payload.get("tags", [])
        tags = [str(item) for item in raw_tags] if isinstance(raw_tags, list) else []
        ingested_at = payload.get("ingested_at")
        return StoredChunk(
            chunk_id=str(payload.get("chunk_id", "")),
            document_id=str(payload.get("document_id", "")),
            title=str(payload.get("title", "")),
            source=payload.get("source") if payload.get("source") else None,
            tags=tags,
            chunk_index=int(payload.get("chunk_index", 0)),
            text=text,
            char_count=int(payload.get("char_count", len(text))),
            ingested_at=str(ingested_at) if ingested_at else None,
        )
