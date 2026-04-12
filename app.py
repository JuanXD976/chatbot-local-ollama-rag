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
from src.routing.router import process_user_message

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

# Inicializar historial
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "Eres un asistente útil, preciso y profesional. "
                "Responde de forma clara, natural y en español. "
                "No inventes datos ni afirmes como reales datos en tiempo real no verificados. "
                "Si no dispones de información fiable, indícalo claramente."
            ),
        }
    ]

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
        
        system_message = next(
                                (msg for msg in st.session_state.messages if msg["role"] == "system"),
                                None
                            )
        recent_messages = st.session_state.messages[-MAX_MESSAGES:]

        if recent_messages[0]["role"] != "system":
            messages_for_model = [system_message] + recent_messages
        else:
            messages_for_model = recent_messages

        reply = process_user_message(prompt, messages_for_model)

        if not reply or reply.strip() == "":
            reply = "⚠️ El modelo no ha devuelto respuesta. Intenta de nuevo."
    
        st.session_state.messages.append({"role": "assistant", "content": reply})

        with st.chat_message("assistant"):
            st.markdown(reply)

    except RequestException as e:
        st.error("Error al comunicarse con Ollama.")
        st.exception(e)

    except KeyError:
        st.error("La respuesta de Ollama no tiene el formato esperado.")

    except Exception as e:
        st.error("Ha ocurrido un error inesperado.")
        st.exception(e)