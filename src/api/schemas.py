from __future__ import annotations

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    mode: str | None = "auto"
    output_format: str | None = "normal"


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    detected_intent: str | None = None
    tools_used: list[str] = []
    sources: list[str] = []
    attachments: list[str] = []
    mode_used: str | None = None
    output_format_used: str | None = None


class SessionMessage(BaseModel):
    role: str
    content: str
    timestamp: str


class SessionSummary(BaseModel):
    session_id: str
    title: str
    created_at: str
    updated_at: str


class SessionDetail(BaseModel):
    session_id: str
    title: str
    created_at: str
    updated_at: str
    messages: list[SessionMessage]


class HealthResponse(BaseModel):
    ok: bool
    ollama_connected: bool
    model: str
    model_available: bool
    document_count: int
    indexed_chunks: int
    vectorstore_exists: bool


class RebuildResponse(BaseModel):
    total_chunks: int


class MemoryResetResponse(BaseModel):
    ok: bool