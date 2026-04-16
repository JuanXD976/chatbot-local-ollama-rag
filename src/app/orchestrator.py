"""
Orquestador central del flujo conversacional.

Motivo de su creación:
- Coordinar el ciclo de petición-respuesta desde un único punto.
- Evitar lógica de negocio dispersa en la UI.
"""

from __future__ import annotations

import logging
from typing import Callable

from src.core.models import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)


class ChatOrchestrator:
    """
    Orquesta el flujo principal de una interacción de chat.
    """

    def __init__(
        self,
        detect_intent_func: Callable[[str], str],
        executor_func: Callable[[str, list[dict[str, str]]], dict],
        stream_executor_func: Callable[[str, list[dict[str, str]]], dict] | None = None,
    ) -> None:
        self.detect_intent_func = detect_intent_func
        self.executor_func = executor_func
        self.stream_executor_func = stream_executor_func

    def handle(self, request: ChatRequest) -> ChatResponse:
        """
        Procesa la petición y devuelve una respuesta estructurada.
        """
        logger.info("Procesando mensaje en sesión %s", request.session_id)

        detected_intent = self.detect_intent_func(request.message)
        logger.info("Intención detectada: %s", detected_intent)

        result = self.executor_func(request.message, request.messages_for_model)

        return ChatResponse(
            answer=result.get("answer", "No se pudo generar una respuesta."),
            detected_intent=result.get("detected_intent", detected_intent),
            tools_used=result.get("tools_used", []),
            sources=result.get("sources", []),
        )

    def stream_handle(self, request: ChatRequest) -> dict:
        """
        Procesa la petición en modo streaming cuando el flujo lo soporta.
        """
        logger.info("Procesando mensaje en streaming en sesión %s", request.session_id)

        if not self.stream_executor_func:
            logger.warning("No hay stream_executor_func configurado; usando executor normal")
            return self.executor_func(request.message, request.messages_for_model)

        detected_intent = self.detect_intent_func(request.message)
        logger.info("Intención detectada (stream): %s", detected_intent)

        result = self.stream_executor_func(request.message, request.messages_for_model)
        if "detected_intent" not in result:
            result["detected_intent"] = detected_intent

        return result