from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户输入")
    system_prompt: str | None = Field(default=None, description="可选系统提示词")


class ChatResponse(BaseModel):
    reply: str
    provider: str
    model: str
    mode: str


class HealthResponse(BaseModel):
    status: str
    provider: str
    model: str
    mode: str
