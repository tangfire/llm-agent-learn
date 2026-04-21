from __future__ import annotations

import hashlib
import logging
import math
import re
import uuid
from datetime import UTC, datetime

from openai import OpenAI, OpenAIError

from app.core.config import Settings
from app.core.errors import ClientInputError, UpstreamServiceError
from app.schemas.document import (
    ChunkConfig,
    ChunkPreview,
    DocumentListResponse,
    DocumentMetadata,
    DocumentTextRequest,
    DocumentTextResponse,
)
from app.schemas.rag import AskRequest, AskResponse, Citation, HealthResponse, RetrievedChunk
from app.services.chunker import TextChunker
from app.services.vector_store import (
    DocumentSummary,
    QdrantVectorStore,
    ScoredChunk,
    StoredChunk,
)

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._chunker = TextChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        self._vector_store = QdrantVectorStore(
            storage_path=settings.qdrant_path,
            collection_name=settings.qdrant_collection_name,
            vector_size=settings.embedding_dimension,
        )
        self._client: OpenAI | None = None

        if settings.openai_api_key:
            self._client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                timeout=settings.openai_timeout,
            )

        logger.info(
            "RAG service initialized | chat_mode=%s | embedding_mode=%s | qdrant=%s",
            self._chat_mode(),
            self._embedding_mode(),
            self._vector_store.describe(),
        )

    def health(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            chat_model=self._settings.chat_model,
            chat_mode=self._chat_mode(),
            embedding_model=self._settings.embedding_model,
            embedding_mode=self._embedding_mode(),
            vector_store=self._vector_store.describe(),
            retrieval_mode="vector-search",
            stored_chunks=self._vector_store.count_chunks(),
            chunk_config=self._chunk_config(),
        )

    def close(self) -> None:
        self._vector_store.close()

    def ingest_text(self, request: DocumentTextRequest) -> DocumentTextResponse:
        document_id = f"doc_{uuid.uuid4().hex[:12]}"
        ingested_at = self._now_isoformat()
        raw_chunks = self._chunker.split_text(request.text)
        if not raw_chunks:
            raise ClientInputError(
                "Document text is empty after trimming.",
                error_code="document_text_empty",
            )

        stored_chunks = [
            StoredChunk(
                chunk_id=f"{document_id}_chunk_{index}",
                document_id=document_id,
                title=request.title,
                source=request.source,
                tags=request.tags,
                chunk_index=index,
                text=chunk_text,
                char_count=len(chunk_text),
                ingested_at=ingested_at,
            )
            for index, chunk_text in enumerate(raw_chunks)
        ]
        embeddings = self._embed_texts([chunk.text for chunk in stored_chunks])
        self._vector_store.upsert_chunks(stored_chunks, embeddings)

        chunk_preview = [
            ChunkPreview(
                chunk_id=chunk.chunk_id,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                char_count=chunk.char_count,
            )
            for chunk in stored_chunks[:3]
        ]

        logger.info(
            "Indexed document | document_id=%s | title=%s | chunk_count=%s",
            document_id,
            request.title,
            len(stored_chunks),
        )
        return DocumentTextResponse(
            document_id=document_id,
            status="indexed",
            title=request.title,
            source=request.source,
            chunk_count=len(stored_chunks),
            chunk_preview=chunk_preview,
            chunk_config=self._chunk_config(),
            ingested_at=ingested_at,
        )

    def list_documents(self) -> DocumentListResponse:
        summaries = self._vector_store.list_documents()
        documents = [self._to_document_metadata(item) for item in summaries]
        logger.info("Listed indexed documents | total=%s", len(documents))
        return DocumentListResponse(
            total_documents=len(documents),
            chunk_config=self._chunk_config(),
            documents=documents,
        )

    def ask(self, request: AskRequest) -> AskResponse:
        query_vector = self._embed_text(request.question)
        candidate_limit = (
            request.top_k if self._client is not None else max(request.top_k * 4, 8)
        )
        retrieved = self._vector_store.retrieve(
            query_vector=query_vector,
            limit=candidate_limit,
        )
        if self._client is None:
            retrieved = self._rerank_locally(request.question, retrieved, request.top_k)
        else:
            retrieved = retrieved[: request.top_k]

        citations = [
            Citation(
                document_id=item.chunk.document_id,
                title=item.chunk.title,
                source=item.chunk.source,
                chunk_id=item.chunk.chunk_id,
                chunk_index=item.chunk.chunk_index,
            )
            for item in retrieved
        ]

        retrieved_chunks = [
            RetrievedChunk(
                chunk_id=item.chunk.chunk_id,
                document_id=item.chunk.document_id,
                title=item.chunk.title,
                source=item.chunk.source,
                chunk_index=item.chunk.chunk_index,
                text=item.chunk.text,
                score=round(item.score, 4),
            )
            for item in retrieved
        ]

        answer = self._build_answer(request.question, retrieved_chunks)
        mode = "live-rag" if self._client is not None else "local-rag"
        logger.info(
            "Answered question | top_k=%s | hits=%s | mode=%s",
            request.top_k,
            len(retrieved_chunks),
            mode,
        )
        return AskResponse(
            answer=answer,
            citations=citations,
            retrieved_chunks=retrieved_chunks,
            mode=mode,
        )

    def _embed_text(self, text: str) -> list[float]:
        return self._embed_texts([text])[0]

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        if self._client is None:
            return [self._local_embedding(text) for text in texts]

        try:
            response = self._client.embeddings.create(
                model=self._settings.embedding_model,
                input=texts,
                dimensions=self._settings.embedding_dimension,
            )
        except OpenAIError as exc:
            raise UpstreamServiceError(
                "Embedding request to OpenAI failed.",
                error_code="embedding_request_failed",
            ) from exc

        sorted_data = sorted(response.data, key=lambda item: item.index)
        return [list(item.embedding) for item in sorted_data]

    def _build_answer(self, question: str, retrieved_chunks: list[RetrievedChunk]) -> str:
        if not retrieved_chunks:
            return "当前还没有检索到可用内容。你可以先通过 /documents/text 导入文档。"

        if self._client is None:
            preview = "；".join(
                f"{item.title} 第 {item.chunk_index} 段：{item.text[:100]}"
                for item in retrieved_chunks
            )
            return (
                f"[local-rag] 问题：{question}。"
                f"当前基于向量检索命中的片段有：{preview}"
            )

        context = "\n\n".join(
            (
                f"[{index}] chunk_id={item.chunk_id}\n"
                f"标题：{item.title}\n"
                f"来源：{item.source or 'unknown'}\n"
                f"内容：{item.text}"
            )
            for index, item in enumerate(retrieved_chunks, start=1)
        )

        try:
            response = self._client.responses.create(
                model=self._settings.chat_model,
                input=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    "你是一个知识库问答助手。"
                                    "只能基于给定检索内容回答，不能编造。"
                                    "如果检索内容不足以回答，就明确说不知道。"
                                    "回答尽量简洁。"
                                ),
                            }
                        ],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    f"问题：{question}\n\n"
                                    f"请基于以下检索内容作答：\n{context}"
                                ),
                            }
                        ],
                    },
                ],
            )
        except OpenAIError as exc:
            raise UpstreamServiceError(
                "Answer generation request to OpenAI failed.",
                error_code="answer_generation_failed",
            ) from exc
        return self._extract_text(response)

    def _local_embedding(self, text: str) -> list[float]:
        dimension = self._settings.embedding_dimension
        vector = [0.0] * dimension
        tokens = self._tokenize(text)
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for index in range(0, len(digest), 4):
                bucket = int.from_bytes(digest[index : index + 4], "little") % dimension
                sign = 1.0 if digest[index] % 2 == 0 else -1.0
                vector[bucket] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector

        return [value / norm for value in vector]

    def _rerank_locally(
        self,
        question: str,
        candidates: list[ScoredChunk],
        limit: int,
    ) -> list[ScoredChunk]:
        query_tokens = self._tokenize(question)
        reranked: list[ScoredChunk] = []
        for item in candidates:
            lexical_score = self._lexical_score(query_tokens, item.chunk.text)
            combined_score = 0.35 * item.score + 0.65 * lexical_score
            reranked.append(ScoredChunk(chunk=item.chunk, score=combined_score))

        reranked.sort(key=lambda item: item.score, reverse=True)
        return reranked[:limit]

    def _lexical_score(self, query_tokens: list[str], text: str) -> float:
        if not query_tokens:
            return 0.0

        text_tokens = set(self._tokenize(text))
        matched_weight = 0.0
        total_weight = 0.0

        for token in set(query_tokens):
            weight = 2.5 if token.isascii() else 1.0
            total_weight += weight
            if token in text_tokens:
                matched_weight += weight

        if total_weight == 0:
            return 0.0
        return matched_weight / total_weight

    def _tokenize(self, text: str) -> list[str]:
        lowered = text.lower()
        tokens = re.findall(r"[a-z0-9_]+", lowered)
        chinese_sequences = re.findall(r"[\u4e00-\u9fff]+", lowered)
        for sequence in chinese_sequences:
            if len(sequence) == 1:
                tokens.append(sequence)
                continue
            tokens.extend(sequence[index : index + 2] for index in range(len(sequence) - 1))
            if len(sequence) >= 3:
                tokens.extend(
                    sequence[index : index + 3] for index in range(len(sequence) - 2)
                )

        if tokens:
            return tokens
        stripped = text.strip().lower()
        return [stripped] if stripped else []

    def _chunk_config(self) -> ChunkConfig:
        return ChunkConfig(
            chunk_size=self._settings.chunk_size,
            chunk_overlap=self._settings.chunk_overlap,
        )

    def _to_document_metadata(self, summary: DocumentSummary) -> DocumentMetadata:
        return DocumentMetadata(
            document_id=summary.document_id,
            title=summary.title,
            source=summary.source,
            tags=summary.tags,
            chunk_count=summary.chunk_count,
            total_char_count=summary.total_char_count,
            ingested_at=summary.ingested_at,
        )

    def _embedding_mode(self) -> str:
        return "openai-embedding" if self._client is not None else "local-hash-embedding"

    def _chat_mode(self) -> str:
        return "openai-response" if self._client is not None else "local-answer"

    def _extract_text(self, response: object) -> str:
        output_text = getattr(response, "output_text", "")
        if output_text:
            return output_text

        parts: list[str] = []
        for item in getattr(response, "output", []) or []:
            for content in getattr(item, "content", []) or []:
                text = getattr(content, "text", "")
                if text:
                    parts.append(text)

        return "".join(parts).strip()

    def _now_isoformat(self) -> str:
        return datetime.now(tz=UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
