from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "RAG Knowledge Assistant")
    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", "8001"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    openai_base_url: str | None = os.getenv("OPENAI_BASE_URL") or None
    openai_timeout: float = float(os.getenv("OPENAI_TIMEOUT", "60"))
    chat_model: str = os.getenv("CHAT_MODEL", "gpt-4.1-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_dimension: int = int(os.getenv("EMBEDDING_DIMENSION", "256"))
    qdrant_path: str = os.getenv("QDRANT_PATH", "./data/qdrant")
    qdrant_collection_name: str = os.getenv(
        "QDRANT_COLLECTION_NAME", "rag_knowledge_base"
    )
    query_trace_path: str = os.getenv(
        "QUERY_TRACE_PATH", "./data/traces/query_traces.jsonl"
    )
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    low_confidence_score_threshold: float = float(
        os.getenv("LOW_CONFIDENCE_SCORE_THRESHOLD", "0.25")
    )


settings = Settings()
