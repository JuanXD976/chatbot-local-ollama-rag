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
from src.core.exceptions import OllamaConnectionError, SessionError
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


def build_services() -> tuple[ChatService, SessionService]:
    """
    Construye las dependencias principales de la aplicación.
    """
    session_service = SessionService(storage_path=SESSION_FILE_PATH)
    orchestrator = ChatOrchestrator(
        detect_intent_func=detect_intent,
        executor_func=execute_user_message,
    )
    chat_service = ChatService(
        session_service=session_service,
        orchestrator=orchestrator,
    )
    return chat_service, session_service


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

    if "selected_session_id" not in st.session_state:
        st.session_state.selected_session_id = st.session_state.session_id


def load_session_into_ui(session_service: SessionService, session_id: str) -> None:
    """
    Carga una sesión persistida dentro de la UI actual.
    """
    session = session_service.get_session(session_id)
    if not session:
        raise SessionError(f"No existe la sesión '{session_id}'.")

    ui_messages = [SYSTEM_MESSAGE]
    for msg in session.messages:
        ui_messages.append({
            "role": msg.role,
            "content": msg.content,
        })

    st.session_state.messages = ui_messages
    st.session_state.session_id = session_id
    st.session_state.selected_session_id = session_id


def start_new_conversation(chat_service: ChatService) -> None:
    """
    Reinicia la conversación actual y crea una nueva sesión persistente.
    """
    new_session_id = chat_service.ensure_session(None)
    st.session_state.messages = [SYSTEM_MESSAGE]
    st.session_state.session_id = new_session_id
    st.session_state.selected_session_id = new_session_id
    st.success("Nueva conversación creada.")
    st.rerun()


def build_messages_for_model() -> list[dict[str, str]]:
    """
    Construye el contexto final que se enviará al modelo.
    """
    session_recent_messages = [
        msg for msg in st.session_state.messages if msg["role"] != "system"
    ][-MAX_MESSAGES:]

    persistent_context = st.session_state.persistent_memory[-4:]
    memory_system_message = build_memory_system_message(persistent_context)

    messages_for_model = [SYSTEM_MESSAGE]

    if memory_system_message:
        messages_for_model.append(memory_system_message)

    messages_for_model.extend(session_recent_messages)
    return messages_for_model


def render_session_sidebar(
    chat_service: ChatService,
    session_service: SessionService,
) -> None:
    """
    Dibuja la gestión visual de sesiones en la barra lateral.
    """
    with st.sidebar:
        st.header("Sesiones")

        if st.button("🆕 Nueva conversación", use_container_width=True):
            start_new_conversation(chat_service)

        sessions = session_service.list_sessions()

        if sessions:
            current_session = session_service.get_session(st.session_state.session_id)

            st.caption(
                f"Sesión activa: {current_session.title if current_session else st.session_state.session_id}"
            )

            for session in sessions:
                is_active = session.session_id == st.session_state.session_id
                title = session.title or "Sin título"
                label = f"🟢 {title}" if is_active else title

                col1, col2 = st.columns([4, 1])

                with col1:
                    if st.button(
                        label,
                        key=f"load_{session.session_id}",
                        use_container_width=True,
                    ):
                        load_session_into_ui(session_service, session.session_id)
                        st.rerun()

                with col2:
                    if st.button(
                        "🗑️",
                        key=f"delete_{session.session_id}",
                        help="Eliminar sesión",
                        use_container_width=True,
                    ):
                        session_service.delete_session(session.session_id)

                        if session.session_id == st.session_state.session_id:
                            new_session_id = chat_service.ensure_session(None)
                            st.session_state.session_id = new_session_id
                            st.session_state.selected_session_id = new_session_id
                            st.session_state.messages = [SYSTEM_MESSAGE]

                        st.success("Sesión eliminada.")
                        st.rerun()

            st.divider()

            export_session = session_service.get_session(st.session_state.session_id)
            if export_session:
                export_json = session_service.export_session_as_json(export_session.session_id)
                safe_title = export_session.title.replace(" ", "_").replace("/", "_")

                st.download_button(
                    label="⬇️ Exportar sesión (JSON)",
                    data=export_json,
                    file_name=f"{safe_title[:40] or 'sesion'}.json",
                    mime="application/json",
                    use_container_width=True,
                )

        else:
            st.info("Todavía no hay sesiones guardadas.")

        st.divider()
        st.header("Memoria")

        if st.button("🧹 Borrar memoria persistente", use_container_width=True):
            reset_persistent_memory()
            st.session_state.persistent_memory = []
            st.success("Memoria persistente borrada correctamente.")
            st.rerun()


def render_chat_messages() -> None:
    """
    Muestra el historial visual del chat actual.
    """
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue

        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_prompt(chat_service: ChatService) -> None:
    """
    Gestiona el input del usuario y el ciclo completo de respuesta.
    """
    prompt = st.chat_input("Escribe tu mensaje...")

    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        messages_for_model = build_messages_for_model()

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

        if any(keyword in prompt.lower() for keyword in [
            "me llamo",
            "mi nombre es",
            "recuerda que",
            "soy",
            "trabajo en",
            "mi empresa es",
        ]):
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


def main() -> None:
    """
    Punto de entrada principal de la aplicación.
    """
    chat_service, session_service = build_services()

    st.set_page_config(page_title="Chatbot V1.3 Local", page_icon="🤖", layout="wide")
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
    render_session_sidebar(chat_service, session_service)
    render_chat_messages()
    handle_user_prompt(chat_service)


if __name__ == "__main__":
    main()