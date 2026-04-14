from __future__ import annotations

import json
from collections.abc import Iterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse, HealthResponse
from app.services.llm import LLMService

router = APIRouter()
llm_service = LLMService(settings)


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        provider=llm_service.provider,
        model=llm_service.model,
        mode=llm_service.mode,
    )


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        reply = llm_service.chat(request)
    except Exception as exc:  # pragma: no cover - minimal starter
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(
        reply=reply,
        provider=llm_service.provider,
        model=llm_service.model,
        mode=llm_service.mode,
    )


@router.post("/stream_chat")
def stream_chat(request: ChatRequest) -> StreamingResponse:
    def event_stream() -> Iterator[str]:
        try:
            for chunk in llm_service.stream_chat(request):
                payload = {"delta": chunk}
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        except Exception as exc:  # pragma: no cover - minimal starter
            payload = {"error": str(exc)}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
