from __future__ import annotations

from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    detected_intent: str
    tools_used: List[str]
    sources: List[str]


class SessionSummary(BaseModel):
    session_id: str
    title: str
    created_at: str
    updated_at: str


class SessionMessage(BaseModel):
    role: str
    content: str
    timestamp: str


class SessionDetail(BaseModel):
    session_id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[SessionMessage]


class UploadResponse(BaseModel):
    path: str
    filename: str


class RebuildResponse(BaseModel):
    total_chunks: int


class MemoryResetResponse(BaseModel):
    ok: bool