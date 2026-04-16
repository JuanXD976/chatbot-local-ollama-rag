"""
Aplicación principal con interfaz Streamlit.

Motivo de su creación:
- Servir como punto de entrada de la aplicación.
- Gestionar la interfaz gráfica y el historial visual del chat.
- Delegar la lógica de generación al router central.
"""

import streamlit as st
from requests.exceptions import RequestException

from src.config.settings import APP_DESCRIPTION, APP_TITLE, OLLAMA_CHAT_MODEL, MAX_MESSAGES
from src.llm.ollama_client import check_ollama_connection
from src.memory.memory_service import (
    append_message_to_memory,
    get_persistent_memory,
    reset_persistent_memory,
)
from src.routing.router import process_user_message

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
    
# Configuración de la página
st.set_page_config(page_title="Chatbot V1 Local", page_icon="🤖")
st.title(APP_TITLE)
st.write(APP_DESCRIPTION)
st.write(f"Modelo local actual: `{OLLAMA_CHAT_MODEL}`")

# Comprobar conexión con Ollama
try:
    ollama_info = check_ollama_connection()
    st.success("Ollama está conectado correctamente.")

    models = [model["name"] for model in ollama_info.get("models", [])]
    
    if OLLAMA_CHAT_MODEL not in models:
        st.warning(
            f"El modelo `{OLLAMA_CHAT_MODEL}` no aparece todavía en Ollama. "
            "Comprueba que está creado e instalado correctamente."
        )
except Exception as e:
    st.error("No se ha podido conectar con Ollama.")
    st.info("Asegúrate de que Ollama está abierto y funcionando.")
    st.exception(e)
    st.stop()
    
# Sidebar de control
with st.sidebar:
    st.header("Memoria")

    if st.button("🧹 Borrar memoria persistente"):
        reset_persistent_memory()
        # Reinicia solo la sesión visual actual
        st.session_state.messages = [SYSTEM_MESSAGE]
        st.session_state.persistent_memory = []

        st.success("Memoria persistente borrada correctamente.")
        st.rerun()

    if st.button("🆕 Nueva conversación"):
        st.session_state.messages = [SYSTEM_MESSAGE]
        st.success("Sesión actual reiniciada.")
        st.rerun()


# Inicialización
if "messages" not in st.session_state:
    # Historial visual de la sesión actual
    st.session_state.messages = [SYSTEM_MESSAGE]

if "persistent_memory" not in st.session_state:
    # Memoria persistente invisible para el usuario
    st.session_state.persistent_memory = get_persistent_memory()

# Mostrar historial
for message in st.session_state.messages:
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
prompt = st.chat_input("Escribe tu mensaje...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        
        session_recent_messages = [
            msg for msg in st.session_state.messages if msg["role"] != "system"
        ][-MAX_MESSAGES:]

        # Memoria persistente previa (solo unos pocos recuerdos)
        persistent_context = st.session_state.persistent_memory[-4:]

        memory_system_message = build_memory_system_message(persistent_context)

        messages_for_model = [SYSTEM_MESSAGE]

        if memory_system_message:
            messages_for_model.append(memory_system_message)

        messages_for_model.extend(session_recent_messages)

        reply = process_user_message(prompt, messages_for_model)

        if not reply or reply.strip() == "":
            reply = "⚠️ El modelo no ha devuelto respuesta. Intenta de nuevo."

        # Añadir respuesta a la sesión visual
        st.session_state.messages.append({"role": "assistant", "content": reply})

        with st.chat_message("assistant"):
            st.markdown(reply)

        # Guardar en memoria persistente después de responder
        append_message_to_memory("user", prompt)

        # Refrescar memoria persistente en la sesión
        st.session_state.persistent_memory = get_persistent_memory()

    except RequestException as e:
        st.error("Error al comunicarse con Ollama.")
        st.exception(e)

    except KeyError:
        st.error("La respuesta de Ollama no tiene el formato esperado.")

    except Exception as e:
        st.error("Ha ocurrido un error inesperado.")
        st.exception(e)