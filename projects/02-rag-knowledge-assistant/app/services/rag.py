from __future__ import annotations

import uuid

from openai import OpenAI

from app.core.config import Settings
from app.schemas.document import ChunkPreview, DocumentTextRequest, DocumentTextResponse
from app.schemas.rag import AskRequest, AskResponse, Citation, HealthResponse, RetrievedChunk
from app.services.chunker import TextChunker
from app.services.vector_store import QdrantVectorStore, StoredChunk, StoredDocument


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
        )
        self._client: OpenAI | None = None

        if settings.openai_api_key:
            self._client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                timeout=settings.openai_timeout,
            )

    def health(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            chat_model=self._settings.chat_model,
            embedding_model=self._settings.embedding_model,
            vector_store=self._vector_store.describe(),
            retrieval_mode="scaffold-preview",
        )

    def close(self) -> None:
        self._vector_store.close()

    def ingest_text(self, request: DocumentTextRequest) -> DocumentTextResponse:
        document_id = f"doc_{uuid.uuid4().hex[:12]}"
        raw_chunks = self._chunker.split_text(request.text)

        stored_chunks = [
            StoredChunk(
                chunk_id=f"{document_id}_chunk_{index}",
                document_id=document_id,
                title=request.title,
                source=request.source,
                chunk_index=index,
                text=chunk_text,
            )
            for index, chunk_text in enumerate(raw_chunks)
        ]

        document = StoredDocument(
            document_id=document_id,
            title=request.title,
            source=request.source,
            tags=request.tags,
            text=request.text,
            chunks=stored_chunks,
        )
        self._vector_store.save_document(document)

        chunk_preview = [
            ChunkPreview(
                chunk_id=chunk.chunk_id,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                char_count=len(chunk.text),
            )
            for chunk in stored_chunks[:3]
        ]

        return DocumentTextResponse(
            document_id=document_id,
            status="accepted",
            title=request.title,
            source=request.source,
            chunk_count=len(stored_chunks),
            chunk_preview=chunk_preview,
        )

    def ask(self, request: AskRequest) -> AskResponse:
        retrieved = self._vector_store.retrieve(query=request.question, limit=request.top_k)

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
        mode = "live-preview" if self._client is not None else "scaffold-preview"

        return AskResponse(
            answer=answer,
            citations=citations,
            retrieved_chunks=retrieved_chunks,
            mode=mode,
        )

    def _build_answer(self, question: str, retrieved_chunks: list[RetrievedChunk]) -> str:
        if not retrieved_chunks:
            return "当前还没有检索到可用内容。你可以先通过 /documents/text 导入文档。"

        if self._client is None:
            preview = "；".join(
                f"{item.title} 第 {item.chunk_index} 段提到：{item.text[:80]}"
                for item in retrieved_chunks
            )
            return f"[scaffold] 问题：{question}。当前命中的片段有：{preview}"

        context = "\n\n".join(
            f"标题：{item.title}\n来源：{item.source or 'unknown'}\n片段：{item.text}"
            for item in retrieved_chunks
        )

        response = self._client.responses.create(
            model=self._settings.chat_model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "你是一个知识库问答助手。只能基于给定检索内容回答，并尽量简洁。",
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"问题：{question}\n\n检索内容：\n{context}",
                        }
                    ],
                },
            ],
        )
        return self._extract_text(response)

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
