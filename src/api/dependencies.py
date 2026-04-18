from __future__ import annotations

from src.app.chat_service import ChatService
from src.app.orchestrator import ChatOrchestrator
from src.app.session_service import SessionService
from src.config.settings import MAX_MESSAGES, SESSION_FILE_PATH
from src.memory.memory_service import get_persistent_memory
from src.routing.router import detect_intent, execute_user_message, stream_user_message

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "Eres un asistente útil, preciso y profesional. "
        "Responde de forma clara, natural y en español. "
        "No inventes datos ni afirmes como reales datos en tiempo real no verificados. "
        "Si no dispones de información fiable, indícalo claramente. "
        "Nunca incluyas prefijos como 'user:', 'assistant:' o etiquetas de rol en tus respuestas."
    ),
}


def build_memory_system_message(memory_messages: list[dict[str, str]]) -> dict[str, str] | None:
    if not memory_messages:
        return None

    memory_lines = []
    for msg in memory_messages:
        content = msg.get("content", "").strip()
        if content:
            memory_lines.append(f"- {content}")

    if not memory_lines:
        return None

    return {
        "role": "system",
        "content": (
            "Memoria persistente del usuario. "
            "Usa esta información solo como contexto útil si es relevante para responder. "
            "No repitas esta memoria literalmente salvo que el usuario pregunte por ella.\n\n"
            + "\n".join(memory_lines)
        ),
    }


def build_services() -> tuple[ChatService, SessionService]:
    session_service = SessionService(storage_path=SESSION_FILE_PATH)
    orchestrator = ChatOrchestrator(
        detect_intent_func=detect_intent,
        executor_func=execute_user_message,
        stream_executor_func=stream_user_message,
    )
    chat_service = ChatService(
        session_service=session_service,
        orchestrator=orchestrator,
    )
    return chat_service, session_service


def build_messages_for_model(
    session_service: SessionService,
    session_id: str,
    current_prompt: str,
) -> list[dict[str, str]]:
    session = session_service.get_session(session_id)

    session_messages = []
    if session:
        session_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in session.messages
        ]

    session_messages.append({"role": "user", "content": current_prompt})
    session_recent_messages = session_messages[-MAX_MESSAGES:]

    persistent_context = get_persistent_memory()[-4:]
    memory_system_message = build_memory_system_message(persistent_context)

    messages_for_model = [SYSTEM_MESSAGE]

    if memory_system_message:
        messages_for_model.append(memory_system_message)

    messages_for_model.extend(session_recent_messages)
    return messages_for_model