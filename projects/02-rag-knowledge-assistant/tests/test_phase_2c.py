from __future__ import annotations

import os
from tempfile import TemporaryDirectory
import unittest

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


class Phase2CTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        qdrant_path = os.path.join(self.temp_dir.name, "qdrant")
        self.app = create_app(
            Settings(
                app_name="RAG Knowledge Assistant Phase 2C Test",
                qdrant_path=qdrant_path,
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
        del self.client
        del self.app
        self.temp_dir.cleanup()

    def test_empty_index_returns_no_hit(self) -> None:
        response = self.client.post(
            "/ask",
            json={
                "question": "Redis 适合做什么？",
                "top_k": 2,
                "return_debug": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "no_hit")
        self.assertEqual(payload["citations"], [])
        self.assertEqual(payload["retrieved_chunks"], [])
        self.assertEqual(payload["debug"]["decision"], "no_hit")
        self.assertEqual(payload["debug"]["rejection_reason"], "knowledge_base_is_empty")

    def test_low_confidence_question_is_rejected(self) -> None:
        self._ingest_redis_document()

        response = self.client.post(
            "/ask",
            json={
                "question": "How do I bake a chiffon cake?",
                "top_k": 2,
                "return_debug": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "low_confidence")
        self.assertEqual(payload["citations"], [])
        self.assertTrue(payload["retrieved_chunks"])
        self.assertEqual(payload["debug"]["decision"], "low_confidence")
        self.assertEqual(payload["debug"]["requested_top_k"], 2)
        self.assertEqual(payload["debug"]["candidate_limit"], 8)
        self.assertLess(payload["debug"]["best_score"], 0.25)
        self.assertEqual(
            payload["debug"]["rejection_reason"],
            "best_score_below_threshold",
        )

    def test_related_question_returns_answer_with_debug(self) -> None:
        self._ingest_redis_document()

        response = self.client.post(
            "/ask",
            json={
                "question": "Redis 常见应用场景有哪些？",
                "top_k": 2,
                "return_debug": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "answered")
        self.assertTrue(payload["citations"])
        self.assertTrue(payload["retrieved_chunks"])
        self.assertEqual(payload["debug"]["decision"], "answered")
        self.assertGreaterEqual(payload["debug"]["best_score"], 0.25)
        self.assertEqual(
            payload["debug"]["low_confidence_score_threshold"],
            0.25,
        )

    def _ingest_redis_document(self) -> None:
        response = self.client.post(
            "/documents/text",
            json={
                "title": "Redis Notes",
                "source": "redis.md",
                "tags": ["cache", "queue"],
                "text": (
                    "Redis 是一个基于内存的数据结构存储系统，"
                    "常用于缓存、消息队列、排行榜、TTL 会话状态和分布式锁。"
                ),
            },
        )
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
