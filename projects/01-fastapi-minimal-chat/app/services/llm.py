from __future__ import annotations

from collections.abc import Iterator

from openai import OpenAI

from app.core.config import Settings
from app.schemas.chat import ChatRequest


class LLMService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: OpenAI | None = None

        requested_provider = settings.llm_provider
        has_openai_key = bool(settings.openai_api_key)

        if requested_provider in {"auto", "openai"} and has_openai_key:
            self.provider = "openai"
            self.mode = "live"
            self.model = settings.llm_model
            self._client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                timeout=settings.openai_timeout,
            )
        elif requested_provider == "openai":
            self.provider = "mock"
            self.mode = "mock-fallback"
            self.model = "mock-echo"
        else:
            self.provider = "mock"
            self.mode = "mock"
            self.model = "mock-echo"

    def chat(self, request: ChatRequest) -> str:
        if self.provider == "mock":
            return self._mock_reply(request)

        if self._client is None:
            raise RuntimeError("OpenAI client is not initialized.")

        response = self._client.responses.create(
            model=self.model,
            input=self._build_input(request),
        )
        return self._extract_text(response)

    def stream_chat(self, request: ChatRequest) -> Iterator[str]:
        if self.provider == "mock":
            reply = self._mock_reply(request)
            chunk_size = 8
            for index in range(0, len(reply), chunk_size):
                yield reply[index : index + chunk_size]
            return

        if self._client is None:
            raise RuntimeError("OpenAI client is not initialized.")

        with self._client.responses.stream(
            model=self.model,
            input=self._build_input(request),
        ) as stream:
            for event in stream:
                if getattr(event, "type", "") == "response.output_text.delta":
                    delta = getattr(event, "delta", "")
                    if delta:
                        yield delta

    def _build_input(self, request: ChatRequest) -> list[dict[str, object]]:
        items: list[dict[str, object]] = []

        if request.system_prompt:
            items.append(
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": request.system_prompt}],
                }
            )

        items.append(
            {
                "role": "user",
                "content": [{"type": "input_text", "text": request.message}],
            }
        )
        return items

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

    def _mock_reply(self, request: ChatRequest) -> str:
        system_hint = f"系统提示词：{request.system_prompt}。 " if request.system_prompt else ""
        return f"[mock] 已收到你的消息。{system_hint}你的输入是：{request.message}"
