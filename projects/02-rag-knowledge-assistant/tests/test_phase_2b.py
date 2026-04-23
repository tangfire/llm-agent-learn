from __future__ import annotations

import os
from tempfile import TemporaryDirectory
import unittest

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


class Phase2BTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        qdrant_path = os.path.join(self.temp_dir.name, "qdrant")
        self.app = create_app(
            Settings(
                app_name="RAG Knowledge Assistant Test",
                qdrant_path=qdrant_path,
                chunk_size=120,
                chunk_overlap=20,
                log_level="INFO",
                openai_api_key=None,
                openai_base_url=None,
            )
        )
        self.client_cm = TestClient(self.app)
        self.client = self.client_cm.__enter__()

    def tearDown(self) -> None:
        self.client_cm.__exit__(None, None, None)
        del self.client
        del self.app
        self.temp_dir.cleanup()

    def test_health_exposes_chunk_config(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["chunk_config"], {"chunk_size": 120, "chunk_overlap": 20})
        self.assertEqual(
            payload["retrieval_config"],
            {
                "low_confidence_score_threshold": 0.25,
                "rerank_enabled": True,
            },
        )

    def test_documents_endpoint_lists_aggregated_metadata(self) -> None:
        ingest_response = self.client.post(
            "/documents/text",
            json={
                "title": "Redis Notes",
                "source": "redis.md",
                "tags": ["cache", "database", "cache"],
                "text": (
                    "Redis is used for cache, queue, and ranking use cases. " * 8
                    + "It can also help with distributed locks."
                ),
            },
        )

        self.assertEqual(ingest_response.status_code, 200)
        ingest_payload = ingest_response.json()
        self.assertEqual(ingest_payload["chunk_config"], {"chunk_size": 120, "chunk_overlap": 20})
        self.assertGreaterEqual(ingest_payload["chunk_count"], 2)
        self.assertTrue(ingest_payload["ingested_at"].endswith("Z"))

        documents_response = self.client.get("/documents")

        self.assertEqual(documents_response.status_code, 200)
        payload = documents_response.json()
        self.assertEqual(payload["total_documents"], 1)
        self.assertEqual(payload["chunk_config"], {"chunk_size": 120, "chunk_overlap": 20})
        self.assertEqual(len(payload["documents"]), 1)
        document = payload["documents"][0]
        self.assertEqual(document["title"], "Redis Notes")
        self.assertEqual(document["source"], "redis.md")
        self.assertEqual(document["tags"], ["cache", "database"])
        self.assertEqual(document["chunk_count"], ingest_payload["chunk_count"])
        self.assertTrue(document["total_char_count"] > 0)
        self.assertTrue(document["ingested_at"].endswith("Z"))

    def test_blank_question_returns_validation_error(self) -> None:
        response = self.client.post(
            "/ask",
            json={
                "question": "   ",
                "top_k": 3,
            },
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
