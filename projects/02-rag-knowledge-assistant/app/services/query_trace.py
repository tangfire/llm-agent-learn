from __future__ import annotations

import json
from pathlib import Path

from app.core.errors import StorageError


class QueryTraceStore:
    def __init__(self, trace_path: str) -> None:
        self._trace_path = Path(trace_path)
        self._trace_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def trace_path(self) -> str:
        return str(self._trace_path)

    def append(self, record: dict[str, object]) -> None:
        try:
            with self._trace_path.open("a", encoding="utf-8") as file:
                json.dump(record, file, ensure_ascii=False)
                file.write("\n")
        except Exception as exc:
            raise StorageError(
                "Failed to append query trace.",
                error_code="query_trace_append_failed",
            ) from exc

    def list_recent(self, limit: int = 20) -> list[dict[str, object]]:
        if limit <= 0:
            return []
        if not self._trace_path.exists():
            return []

        try:
            lines = [
                line.strip()
                for line in self._trace_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            selected = lines[-limit:]
            records: list[dict[str, object]] = []
            for line in reversed(selected):
                parsed = json.loads(line)
                if not isinstance(parsed, dict):
                    raise ValueError("Trace line must be a JSON object.")
                records.append(parsed)
            return records
        except Exception as exc:
            raise StorageError(
                "Failed to read query traces.",
                error_code="query_trace_read_failed",
            ) from exc
