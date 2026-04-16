"""
Cliente para conectarse a la API local de Ollama.

Motivo de su creación:
- Centralizar la conexión con Ollama.
- Evitar repetir la URL base en varios archivos.
- Facilitar cambios futuros en la configuración.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

import requests

from src.config.settings import OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL
from src.core.exceptions import OllamaConnectionError

logger = logging.getLogger(__name__)


def check_ollama_connection() -> dict:
    """
    Comprueba si Ollama está accesible consultando los modelos locales.
    """
    url = f"{OLLAMA_BASE_URL}/api/tags"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise OllamaConnectionError(
            "No se pudo conectar con Ollama. Comprueba que el servicio esté levantado."
        ) from exc


def clean_response(text: Optional[str]) -> str:
    """
    Limpia la respuesta generada por el modelo eliminando tokens internos,
    etiquetas técnicas y espacios sobrantes.
    """
    if not text:
        return ""

    if not isinstance(text, str):
        text = str(text)

    exact_tokens = [
        "<file_separator>",
        "<|file_separator|>",
        "<s>",
        "</s>",
        "<bos>",
        "<eos>",
    ]

    for token in exact_tokens:
        text = text.replace(token, "")

    text = re.sub(r"<\|[^>]+\|>", "", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def generate_response(messages: list[dict[str, str]], max_tokens: int = 700) -> str:
    """
    Envía el historial de mensajes al endpoint /api/chat de Ollama
    y devuelve el contenido textual de la respuesta.
    """
    url = f"{OLLAMA_BASE_URL}/api/chat"

    payload = {
        "model": OLLAMA_CHAT_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
        },
    }
    try:
        logger.info("Enviando petición a Ollama con %s mensajes", len(messages))
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        message = data.get("message", {})
        content = message.get("content", "")

        cleaned = clean_response(content)
        logger.info("Respuesta recibida correctamente desde Ollama")
        return cleaned

    except requests.RequestException as exc:
        logger.exception("Fallo al comunicarse con Ollama")
        raise OllamaConnectionError(
            f"No se pudo obtener respuesta del modelo local: {exc}"
        ) from exc


def format_tool_result_with_llm(user_prompt: str, tool_name: str, tool_result: str) -> str:
    """
    Usa el modelo para transformar el resultado crudo de una tool
    en una respuesta clara, natural y útil para el usuario.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "Eres un asistente preciso y profesional. "
                "Tu tarea es transformar resultados de herramientas en respuestas finales claras, "
                "naturales y útiles en español. "
                "No inventes datos. "
                "No modifiques fechas ni datos numéricos. "
                "No inventes días de la semana. "
                "Usa solo la información proporcionada por la herramienta. "
                "Si la información está en inglés, tradúcela al español. "
                "Mejora la redacción y el formato, pero no elimines información importante. "
                "Si la herramienta devuelve una lista completa de elementos, como varios días de una previsión, "
                "debes incluirlos todos. "
                "No menciones nombres internos como 'tool', 'router', 'API' o 'tool_result'."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Consulta original del usuario: {user_prompt}\n\n"
                f"Herramienta utilizada: {tool_name}\n\n"
                f"Resultado de la herramienta:\n{tool_result}\n\n"
                "Redacta una respuesta final para el usuario en español."
            ),
        },
    ]

    return generate_response(messages)