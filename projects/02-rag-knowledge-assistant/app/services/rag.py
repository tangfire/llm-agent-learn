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
    DocumentFilePathRequest,
    DocumentListResponse,
    DocumentMetadata,
    DocumentTextRequest,
    DocumentTextResponse,
    IngestStrategy,
)
from app.schemas.rag import (
    AskRequest,
    AskResponse,
    Citation,
    HealthResponse,
    QueryTraceListResponse,
    QueryTraceSummary,
    RetrievalConfig,
    RetrievalDebug,
    RetrievedChunk,
)
from app.services.chunker import TextChunker
from app.services.document_loader import LocalDocumentLoader
from app.services.query_trace import QueryTraceStore
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
        self._query_trace_store = QueryTraceStore(settings.query_trace_path)
        self._document_loader = LocalDocumentLoader()
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
            retrieval_config=self._retrieval_config(),
        )

    def close(self) -> None:
        self._vector_store.close()

    def ingest_text(self, request: DocumentTextRequest) -> DocumentTextResponse:
        return self._ingest_document(
            title=request.title,
            text=request.text,
            source=request.source,
            source_type="inline_text",
            tags=request.tags,
            ingest_strategy=request.ingest_strategy,
        )

    def ingest_file_path(self, request: DocumentFilePathRequest) -> DocumentTextResponse:
        loaded = self._document_loader.load(
            request.path,
            title=request.title,
            source=request.source,
        )
        return self._ingest_document(
            title=loaded.title,
            text=loaded.text,
            source=loaded.source,
            source_type=loaded.source_type,
            tags=request.tags,
            ingest_strategy=request.ingest_strategy,
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

    def list_query_traces(self, limit: int = 20) -> QueryTraceListResponse:
        records = self._query_trace_store.list_recent(limit=limit)
        traces = [QueryTraceSummary(**record) for record in records]
        return QueryTraceListResponse(total=len(traces), traces=traces)

    def ask(self, request: AskRequest) -> AskResponse:
        query_vector = self._embed_text(request.question)
        candidate_limit = (
            request.top_k if self._client is not None else max(request.top_k * 4, 8)
        )
        retrieved = self._vector_store.retrieve(
            query_vector=query_vector,
            limit=candidate_limit,
            document_ids=request.document_ids,
            tags=request.tags,
        )
        rerank_applied = self._client is None
        if rerank_applied:
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

        decision, rejection_reason = self._evaluate_retrieval(
            retrieved_chunks,
            has_filters=bool(request.document_ids or request.tags),
        )
        if decision == "answered":
            answer = self._build_answer(request.question, retrieved_chunks)
        else:
            answer = self._build_rejection_answer(rejection_reason)

        mode = "live-rag" if self._client is not None else "local-rag"
        trace_id = self._export_query_trace(
            question=request.question,
            mode=mode,
            status=decision,
            requested_top_k=request.top_k,
            candidate_limit=candidate_limit,
            filtered_document_ids=request.document_ids,
            filtered_tags=request.tags,
            retrieved_count=len(retrieved_chunks),
            best_score=retrieved_chunks[0].score if retrieved_chunks else None,
            rejection_reason=rejection_reason,
            citations=citations,
            answer=answer,
            retrieved_chunks=retrieved_chunks,
        )

        debug = RetrievalDebug(
            requested_top_k=request.top_k,
            candidate_limit=candidate_limit,
            rerank_applied=rerank_applied,
            low_confidence_score_threshold=self._settings.low_confidence_score_threshold,
            retrieved_count=len(retrieved_chunks),
            filtered_document_ids=request.document_ids,
            filtered_tags=request.tags,
            best_score=retrieved_chunks[0].score if retrieved_chunks else None,
            decision=decision,
            rejection_reason=rejection_reason,
            trace_id=trace_id,
        )
        logger.info(
            "Handled question | top_k=%s | hits=%s | mode=%s | decision=%s | doc_filters=%s | tag_filters=%s",
            request.top_k,
            len(retrieved_chunks),
            mode,
            decision,
            len(request.document_ids),
            len(request.tags),
        )
        return AskResponse(
            status=decision,
            answer=answer,
            citations=citations if decision == "answered" else [],
            retrieved_chunks=retrieved_chunks,
            mode=mode,
            debug=debug if request.return_debug or decision != "answered" else None,
        )

    def _ingest_document(
        self,
        *,
        title: str,
        text: str,
        source: str | None,
        source_type: str,
        tags: list[str],
        ingest_strategy: IngestStrategy,
    ) -> DocumentTextResponse:
        normalized_text = text.strip()
        if not normalized_text:
            raise ClientInputError(
                "Document text is empty after trimming.",
                error_code="document_text_empty",
            )

        content_sha256 = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
        dedupe_action = self._apply_ingest_strategy(
            source=source,
            content_sha256=content_sha256,
            ingest_strategy=ingest_strategy,
        )

        document_id = f"doc_{uuid.uuid4().hex[:12]}"
        ingested_at = self._now_isoformat()
        raw_chunks = self._chunker.split_text(normalized_text)
        if not raw_chunks:
            raise ClientInputError(
                "Document text is empty after trimming.",
                error_code="document_text_empty",
            )

        stored_chunks = [
            StoredChunk(
                chunk_id=f"{document_id}_chunk_{index}",
                document_id=document_id,
                title=title,
                source=source,
                source_type=source_type,
                tags=tags,
                chunk_index=index,
                text=chunk_text,
                char_count=len(chunk_text),
                content_sha256=content_sha256,
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
            "Indexed document | document_id=%s | title=%s | chunk_count=%s | dedupe_action=%s",
            document_id,
            title,
            len(stored_chunks),
            dedupe_action,
        )
        return DocumentTextResponse(
            document_id=document_id,
            status="indexed",
            title=title,
            source=source,
            source_type=source_type,
            chunk_count=len(stored_chunks),
            chunk_preview=chunk_preview,
            chunk_config=self._chunk_config(),
            ingested_at=ingested_at,
            dedupe_action=dedupe_action,
            ingest_strategy=ingest_strategy,
        )

    def _apply_ingest_strategy(
        self,
        *,
        source: str | None,
        content_sha256: str,
        ingest_strategy: IngestStrategy,
    ) -> str:
        conflicts = self._collect_conflicting_documents(
            source=source,
            content_sha256=content_sha256,
        )
        if not conflicts:
            return "inserted"

        if ingest_strategy == IngestStrategy.KEEP_BOTH:
            return "kept_both"

        if ingest_strategy == IngestStrategy.REJECT_DUPLICATE:
            raise ClientInputError(
                "A document with the same source or content already exists.",
                error_code="document_duplicate_rejected",
            )

        deleted_count = self._vector_store.delete_documents(
            [item.document_id for item in conflicts]
        )
        logger.info(
            "Replaced existing documents before ingest | source=%s | deleted_documents=%s",
            source,
            deleted_count,
        )
        return "replaced_existing"

    def _collect_conflicting_documents(
        self,
        *,
        source: str | None,
        content_sha256: str,
    ) -> list[DocumentSummary]:
        aggregated: dict[str, DocumentSummary] = {}
        if source:
            for item in self._vector_store.find_documents(source=source):
                aggregated[item.document_id] = item
        for item in self._vector_store.find_documents(content_sha256=content_sha256):
            aggregated[item.document_id] = item
        return list(aggregated.values())

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

    def _export_query_trace(
        self,
        *,
        question: str,
        mode: str,
        status: str,
        requested_top_k: int,
        candidate_limit: int,
        filtered_document_ids: list[str],
        filtered_tags: list[str],
        retrieved_count: int,
        best_score: float | None,
        rejection_reason: str | None,
        citations: list[Citation],
        answer: str,
        retrieved_chunks: list[RetrievedChunk],
    ) -> str | None:
        trace_id = f"trace_{uuid.uuid4().hex[:12]}"
        record = {
            "trace_id": trace_id,
            "created_at": self._now_isoformat(),
            "question": question,
            "status": status,
            "mode": mode,
            "requested_top_k": requested_top_k,
            "candidate_limit": candidate_limit,
            "filtered_document_ids": filtered_document_ids,
            "filtered_tags": filtered_tags,
            "retrieved_count": retrieved_count,
            "best_score": best_score,
            "rejection_reason": rejection_reason,
            "citations": [item.model_dump() for item in citations],
            "answer_preview": answer[:240],
            "retrieved_chunks": [item.model_dump() for item in retrieved_chunks],
        }
        try:
            self._query_trace_store.append(record)
        except Exception:
            logger.warning(
                "Failed to export query trace | trace_path=%s",
                self._query_trace_store.trace_path,
                exc_info=True,
            )
            return None
        return trace_id

    def _to_document_metadata(self, summary: DocumentSummary) -> DocumentMetadata:
        return DocumentMetadata(
            document_id=summary.document_id,
            title=summary.title,
            source=summary.source,
            source_type=summary.source_type,
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

    def _retrieval_config(self) -> RetrievalConfig:
        return RetrievalConfig(
            low_confidence_score_threshold=self._settings.low_confidence_score_threshold,
            rerank_enabled=self._client is None,
        )

    def _evaluate_retrieval(
        self,
        retrieved_chunks: list[RetrievedChunk],
        *,
        has_filters: bool,
    ) -> tuple[str, str | None]:
        if not retrieved_chunks:
            if has_filters:
                return "no_hit", "no_chunks_after_filter"
            if self._vector_store.count_chunks() == 0:
                return "no_hit", "knowledge_base_is_empty"
            return "no_hit", "no_chunks_retrieved"

        best_score = retrieved_chunks[0].score
        if best_score < self._settings.low_confidence_score_threshold:
            return "low_confidence", "best_score_below_threshold"
        return "answered", None

    def _build_rejection_answer(self, rejection_reason: str | None) -> str:
        if rejection_reason == "knowledge_base_is_empty":
            return "我没有在知识库里检索到可用内容。你可以先导入文档，或者换一种问法再试。"
        if rejection_reason == "no_chunks_after_filter":
            return (
                "当前过滤条件把检索范围收得太窄了，所以没有命中任何片段。"
                "你可以放宽 tags 或 document_ids 条件后再试。"
            )
        return (
            "我检索到了一些片段，但相关度不够高，当前不适合直接给结论。"
            "你可以换一种更具体的问法，或先补充更相关的文档。"
        )
