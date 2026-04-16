"""
Modelos internos de la aplicación.

Motivo de su creación:
- Estandarizar estructuras internas.
- Reducir uso de diccionarios sueltos.
- Preparar el proyecto para futura API y frontend desacoplado.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List


@dataclass
class ChatMessage:
    """
    Representa un mensaje de una conversación.
    """
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ChatSession:
    """
    Representa una sesión conversacional persistente.
    """
    session_id: str
    title: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    messages: List[ChatMessage] = field(default_factory=list)


@dataclass
class ChatRequest:
    """
    Petición de chat hacia la capa de aplicación.
    """
    message: str
    session_id: str
    messages_for_model: List[dict[str, str]] = field(default_factory=list)


@dataclass
class ChatResponse:
    """
    Respuesta estructurada de la aplicación.
    """
    answer: str
    detected_intent: str = "chat"
    tools_used: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())