from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


class HardeningTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        qdrant_path = os.path.join(self.temp_dir.name, "qdrant")
        self.app = create_app(
            Settings(
                app_name="RAG Knowledge Assistant Hardening Test",
                qdrant_path=qdrant_path,
                query_trace_path=os.path.join(self.temp_dir.name, "query_traces.jsonl"),
                chunk_size=180,
                chunk_overlap=30,
                log_level="INFO",
                openai_api_key=None,
                openai_base_url=None,
                low_confidence_score_threshold=0.25,
            )
        )
        self.client_cm = TestClient(self.app)
        self.client = self.client_cm.__enter__()

    def tearDown(self) -> None:
        self.client_cm.__exit__(None, None, None)
        self.temp_dir.cleanup()

    def test_ask_can_filter_by_tags_and_document_ids(self) -> None:
        redis_id = self._ingest_document(
            title="Redis Notes",
            source="redis.md",
            tags=["cache", "queue"],
            text="Redis 常用于缓存、消息队列、排行榜和分布式锁。",
        )
        postgres_id = self._ingest_document(
            title="PostgreSQL Notes",
            source="postgres.md",
            tags=["database"],
            text="PostgreSQL 的 MVCC 可以减少高并发读写场景下的锁冲突。",
        )

        scoped_response = self.client.post(
            "/ask",
            json={
                "question": "PostgreSQL 的 MVCC 有什么作用？",
                "document_ids": [postgres_id],
                "tags": ["database"],
                "return_debug": True,
            },
        )
        self.assertEqual(scoped_response.status_code, 200)
        scoped_payload = scoped_response.json()
        self.assertEqual(scoped_payload["status"], "answered")
        self.assertEqual(scoped_payload["citations"][0]["title"], "PostgreSQL Notes")
        self.assertEqual(scoped_payload["debug"]["filtered_document_ids"], [postgres_id])
        self.assertEqual(scoped_payload["debug"]["filtered_tags"], ["database"])

        narrowed_response = self.client.post(
            "/ask",
            json={
                "question": "Redis 常见应用场景有哪些？",
                "document_ids": [postgres_id],
                "tags": ["database"],
                "return_debug": True,
            },
        )
        self.assertEqual(narrowed_response.status_code, 200)
        narrowed_payload = narrowed_response.json()
        self.assertIn(narrowed_payload["status"], {"no_hit", "low_confidence"})
        self.assertNotEqual(
            narrowed_payload["debug"]["filtered_document_ids"],
            [redis_id],
        )

    def test_replace_existing_prevents_duplicate_pollution(self) -> None:
        first_response = self.client.post(
            "/documents/text",
            json={
                "title": "Redis Notes",
                "source": "redis.md",
                "tags": ["cache"],
                "text": "Redis 常用于缓存。",
            },
        )
        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(first_response.json()["dedupe_action"], "inserted")

        second_response = self.client.post(
            "/documents/text",
            json={
                "title": "Redis Notes",
                "source": "redis.md",
                "tags": ["cache", "stream"],
                "text": "Redis Streams 可以用于事件流和异步任务编排。",
            },
        )
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(second_response.json()["dedupe_action"], "replaced_existing")

        documents_response = self.client.get("/documents")
        self.assertEqual(documents_response.status_code, 200)
        payload = documents_response.json()
        self.assertEqual(payload["total_documents"], 1)
        self.assertEqual(payload["documents"][0]["tags"], ["cache", "stream"])

        ask_response = self.client.post(
            "/ask",
            json={
                "question": "Redis Streams 可以做什么？",
                "return_debug": True,
            },
        )
        self.assertEqual(ask_response.status_code, 200)
        ask_payload = ask_response.json()
        self.assertEqual(ask_payload["status"], "answered")
        self.assertIn("Streams", ask_payload["retrieved_chunks"][0]["text"])

    def test_reject_duplicate_can_block_repeated_ingest(self) -> None:
        first_response = self.client.post(
            "/documents/text",
            json={
                "title": "FastAPI Notes",
                "source": "fastapi.md",
                "text": "FastAPI 适合做 Python API 服务。",
            },
        )
        self.assertEqual(first_response.status_code, 200)

        duplicate_response = self.client.post(
            "/documents/text",
            json={
                "title": "FastAPI Notes",
                "source": "fastapi.md",
                "text": "FastAPI 适合做 Python API 服务。",
                "ingest_strategy": "reject_duplicate",
            },
        )
        self.assertEqual(duplicate_response.status_code, 400)
        self.assertEqual(
            duplicate_response.json()["error"]["code"],
            "document_duplicate_rejected",
        )

    def test_file_path_ingest_supports_csv(self) -> None:
        csv_path = Path(self.temp_dir.name) / "kb.csv"
        csv_path.write_text(
            "product,use_case\nRedis,缓存和排行榜\nQdrant,向量检索和 metadata filtering\n",
            encoding="utf-8",
        )

        ingest_response = self.client.post(
            "/documents/file-path",
            json={
                "path": str(csv_path),
                "tags": ["table", "ingest"],
            },
        )
        self.assertEqual(ingest_response.status_code, 200)
        payload = ingest_response.json()
        self.assertEqual(payload["source_type"], "file:.csv")

        ask_response = self.client.post(
            "/ask",
            json={
                "question": "Qdrant 支持什么过滤能力？",
                "tags": ["table"],
                "return_debug": True,
            },
        )
        self.assertEqual(ask_response.status_code, 200)
        ask_payload = ask_response.json()
        self.assertEqual(ask_payload["status"], "answered")
        self.assertEqual(ask_payload["citations"][0]["source"], str(csv_path))

    def _ingest_document(
        self,
        *,
        title: str,
        source: str,
        tags: list[str],
        text: str,
    ) -> str:
        response = self.client.post(
            "/documents/text",
            json={
                "title": title,
                "source": source,
                "tags": tags,
                "text": text,
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["document_id"]


if __name__ == "__main__":
    unittest.main()
