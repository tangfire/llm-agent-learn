from __future__ import annotations


class TextChunker:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self._chunk_size = max(100, chunk_size)
        self._chunk_overlap = max(0, min(chunk_overlap, self._chunk_size - 1))

    def split_text(self, text: str) -> list[str]:
        content = text.strip()
        if not content:
            return []

        chunks: list[str] = []
        start = 0
        content_length = len(content)

        while start < content_length:
            end = min(content_length, start + self._chunk_size)
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)

            if end >= content_length:
                break

            next_start = end - self._chunk_overlap
            start = next_start if next_start > start else end

        return chunks
