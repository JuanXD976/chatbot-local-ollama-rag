"""
Aplicación principal con interfaz Streamlit.

Motivo de su creación:
- Servir como punto de entrada de la aplicación.
- Gestionar la interfaz gráfica y el historial visual del chat.
- Delegar la lógica de negocio a servicios de aplicación.
"""

from __future__ import annotations

import logging

import streamlit as st
from requests.exceptions import RequestException

from src.app.chat_service import ChatService
from src.app.orchestrator import ChatOrchestrator
from src.app.session_service import SessionService
from src.config.logging_config import configure_logging
from src.config.settings import (
    APP_DESCRIPTION,
    APP_TITLE,
    LOG_LEVEL,
    MAX_MESSAGES,
    OLLAMA_CHAT_MODEL,
    SESSION_FILE_PATH,
)
from src.core.exceptions import OllamaConnectionError
from src.llm.ollama_client import check_ollama_connection
from src.memory.memory_service import (
    append_message_to_memory,
    get_persistent_memory,
    reset_persistent_memory,
)
from src.routing.router import detect_intent, execute_user_message

configure_logging(LOG_LEVEL)
logger = logging.getLogger(__name__)

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
    """
    Convierte la memoria persistente en un bloque de contexto interno para el modelo.
    """
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


def build_services() -> ChatService:
    """
    Construye las dependencias principales de la aplicación.
    """
    session_service = SessionService(storage_path=SESSION_FILE_PATH)
    orchestrator = ChatOrchestrator(
        detect_intent_func=detect_intent,
        executor_func=execute_user_message,
    )
    return ChatService(
        session_service=session_service,
        orchestrator=orchestrator,
    )


def initialize_session_state(chat_service: ChatService) -> None:
    """
    Inicializa el estado de sesión visual y conversacional.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = [SYSTEM_MESSAGE]

    if "persistent_memory" not in st.session_state:
        st.session_state.persistent_memory = get_persistent_memory()

    if "session_id" not in st.session_state:
        st.session_state.session_id = chat_service.ensure_session(None)


def start_new_conversation(chat_service: ChatService) -> None:
    """
    Reinicia la conversación actual y crea una nueva sesión persistente.
    """
    st.session_state.messages = [SYSTEM_MESSAGE]
    st.session_state.session_id = chat_service.ensure_session(None)
    st.success("Sesión actual reiniciada.")
    st.rerun()


def main() -> None:
    """
    Punto de entrada principal de la aplicación.
    """
    chat_service = build_services()

    st.set_page_config(page_title="Chatbot V1.2 Local", page_icon="🤖")
    st.title(APP_TITLE)
    st.write(APP_DESCRIPTION)
    st.write(f"Modelo local actual: `{OLLAMA_CHAT_MODEL}`")

    try:
        ollama_info = check_ollama_connection()
        st.success("Ollama está conectado correctamente.")

        models = [model["name"] for model in ollama_info.get("models", [])]

        if OLLAMA_CHAT_MODEL not in models:
            st.warning(
                f"El modelo `{OLLAMA_CHAT_MODEL}` no aparece todavía en Ollama. "
                "Comprueba que está creado e instalado correctamente."
            )

    except OllamaConnectionError as exc:
        st.error("No se ha podido conectar con Ollama.")
        st.info("Asegúrate de que Ollama está abierto y funcionando.")
        st.exception(exc)
        st.stop()

    initialize_session_state(chat_service)

    with st.sidebar:
        st.header("Memoria y sesión")

        st.caption(f"Session ID: {st.session_state.session_id}")

        if st.button("🧹 Borrar memoria persistente"):
            reset_persistent_memory()
            st.session_state.messages = [SYSTEM_MESSAGE]
            st.session_state.persistent_memory = []
            st.success("Memoria persistente borrada correctamente.")
            st.rerun()

        if st.button("🆕 Nueva conversación"):
            start_new_conversation(chat_service)

    for message in st.session_state.messages:
        if message["role"] == "system":
            continue

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Escribe tu mensaje...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            session_recent_messages = [
                msg for msg in st.session_state.messages if msg["role"] != "system"
            ][-MAX_MESSAGES:]

            persistent_context = st.session_state.persistent_memory[-4:]
            memory_system_message = build_memory_system_message(persistent_context)

            messages_for_model = [SYSTEM_MESSAGE]

            if memory_system_message:
                messages_for_model.append(memory_system_message)

            messages_for_model.extend(session_recent_messages)

            response = chat_service.process_message(
                session_id=st.session_state.session_id,
                user_message=prompt,
                messages_for_model=messages_for_model,
            )

            reply = response.answer.strip() if response.answer else ""

            if not reply:
                reply = "⚠️ El modelo no ha devuelto respuesta. Intenta de nuevo."

            st.session_state.messages.append({"role": "assistant", "content": reply})

            with st.chat_message("assistant"):
                st.markdown(reply)

            append_message_to_memory("user", prompt)
            st.session_state.persistent_memory = get_persistent_memory()

            logger.info(
                "Respuesta emitida | intent=%s | tools=%s",
                response.detected_intent,
                response.tools_used,
            )

        except RequestException as exc:
            logger.exception("Error de comunicación con Ollama")
            st.error("Error al comunicarse con Ollama.")
            st.exception(exc)

        except KeyError as exc:
            logger.exception("Formato inesperado de respuesta")
            st.error("La respuesta de Ollama no tiene el formato esperado.")
            st.exception(exc)

        except Exception as exc:
            logger.exception("Error inesperado en app.py")
            st.error("Ha ocurrido un error inesperado.")
            st.exception(exc)


if __name__ == "__main__":
    main()