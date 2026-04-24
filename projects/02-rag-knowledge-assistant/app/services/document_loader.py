from __future__ import annotations

from csv import DictReader
from dataclasses import dataclass
import html
import json
from pathlib import Path
import re

from app.core.errors import ClientInputError


TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".markdown",
    ".log",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class LoadedDocument:
    title: str
    source: str
    source_type: str
    text: str


class LocalDocumentLoader:
    def load(
        self,
        path: str,
        *,
        title: str | None = None,
        source: str | None = None,
    ) -> LoadedDocument:
        file_path = Path(path).expanduser()
        if not file_path.exists():
            raise ClientInputError(
                f"File does not exist: {file_path}",
                error_code="document_file_not_found",
            )
        if not file_path.is_file():
            raise ClientInputError(
                f"Path is not a file: {file_path}",
                error_code="document_file_invalid_path",
            )

        suffix = file_path.suffix.lower()
        resolved_text = self._load_text(file_path, suffix)
        normalized_text = resolved_text.strip()
        if not normalized_text:
            raise ClientInputError(
                f"Loaded file is empty after normalization: {file_path.name}",
                error_code="document_file_empty",
            )

        return LoadedDocument(
            title=title or file_path.stem,
            source=source or str(file_path),
            source_type=f"file:{suffix or 'unknown'}",
            text=normalized_text,
        )

    def supported_formats(self) -> list[str]:
        return sorted(TEXT_EXTENSIONS | {".csv", ".json", ".jsonl", ".html", ".htm"})

    def _load_text(self, file_path: Path, suffix: str) -> str:
        if suffix in TEXT_EXTENSIONS:
            return self._read_text(file_path)
        if suffix == ".json":
            return self._load_json(file_path)
        if suffix == ".jsonl":
            return self._load_jsonl(file_path)
        if suffix == ".csv":
            return self._load_csv(file_path)
        if suffix in {".html", ".htm"}:
            return self._load_html(file_path)

        raise ClientInputError(
            (
                f"Unsupported file type: {suffix or '[no extension]'}. "
                "Current loader supports: "
                f"{', '.join(self.supported_formats())}."
            ),
            error_code="document_file_unsupported_type",
        )

    def _read_text(self, file_path: Path) -> str:
        for encoding in ("utf-8", "utf-8-sig", "gb18030"):
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue

        raise ClientInputError(
            f"Unable to decode text file: {file_path.name}",
            error_code="document_file_decode_failed",
        )

    def _load_json(self, file_path: Path) -> str:
        content = self._read_text(file_path)
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ClientInputError(
                f"Invalid JSON file: {file_path.name}",
                error_code="document_file_invalid_json",
            ) from exc
        return json.dumps(parsed, ensure_ascii=False, indent=2)

    def _load_jsonl(self, file_path: Path) -> str:
        lines = self._read_text(file_path).splitlines()
        normalized_lines: list[str] = []
        for index, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ClientInputError(
                    f"Invalid JSONL at line {index}: {file_path.name}",
                    error_code="document_file_invalid_jsonl",
                ) from exc
            normalized_lines.append(f"[line {index}] {json.dumps(parsed, ensure_ascii=False)}")
        return "\n".join(normalized_lines)

    def _load_csv(self, file_path: Path) -> str:
        content = self._read_text(file_path).splitlines()
        if not content:
            return ""

        reader = DictReader(content)
        rows: list[str] = []
        for index, row in enumerate(reader, start=1):
            rendered = " | ".join(f"{key}: {value}" for key, value in row.items())
            rows.append(f"[row {index}] {rendered}")
        if rows:
            return "\n".join(rows)

        return "\n".join(content)

    def _load_html(self, file_path: Path) -> str:
        raw = self._read_text(file_path)
        without_scripts = re.sub(
            r"<(script|style)\b[^>]*>.*?</\1>",
            " ",
            raw,
            flags=re.IGNORECASE | re.DOTALL,
        )
        without_tags = re.sub(r"<[^>]+>", " ", without_scripts)
        normalized = html.unescape(without_tags)
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized.strip()
