"""
Servicio principal de conversación.

Motivo de su creación:
- Encapsular sesiones y orquestación.
- Exponer una interfaz limpia hacia la UI.
"""

from __future__ import annotations

import logging

from src.app.orchestrator import ChatOrchestrator
from src.app.session_service import SessionService
from src.core.models import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)


class ChatService:
    """
    Servicio de alto nivel para procesar mensajes de usuario.
    """

    def __init__(
        self,
        session_service: SessionService,
        orchestrator: ChatOrchestrator,
    ) -> None:
        self.session_service = session_service
        self.orchestrator = orchestrator

    def ensure_session(self, session_id: str | None) -> str:
        """
        Garantiza que exista una sesión válida.
        """
        if session_id:
            existing = self.session_service.get_session(session_id)
            if existing:
                return existing.session_id

        new_session = self.session_service.create_session()
        logger.info("Creada nueva sesión: %s", new_session.session_id)
        return new_session.session_id

    def process_message(
        self,
        session_id: str,
        user_message: str,
        messages_for_model: list[dict[str, str]],
    ) -> ChatResponse:
        """
        Procesa un mensaje dentro de una sesión.
        """
        self.session_service.append_message(session_id, "user", user_message)

        request = ChatRequest(
            message=user_message,
            session_id=session_id,
            messages_for_model=messages_for_model,
        )

        response = self.orchestrator.handle(request)

        self.session_service.append_message(session_id, "assistant", response.answer)

        return response