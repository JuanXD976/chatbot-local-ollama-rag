"""
Cliente para conectarse a la API local de Ollama.

Motivo de su creación:
- Centralizar la conexión con Ollama.
- Evitar repetir la URL base en varios archivos.
- Facilitar cambios futuros en la configuración.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Generator, Optional

import requests

from src.config.settings import OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL, OLLAMA_MAX_TOKENS
from src.core.exceptions import OllamaConnectionError

logger = logging.getLogger(__name__)


STREAM_EXACT_TOKENS = [
    "<file_separator>",
    "<|file_separator|>",
    "<s>",
    "</s>",
    "<bos>",
    "<eos>",
    "<im_start>",
    "<im_end>",
    "system>",
    "assistant>",
    "user>",
]


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

    for token in STREAM_EXACT_TOKENS:
        text = text.replace(token, "")

    # tokens estilo <|...|>
    text = re.sub(r"<\|[^>]+\|>", "", text)

    # tokens estilo <im_start>, <im_end>, etc.
    text = re.sub(r"<[a-zA-Z0-9_\/\-]+>", "", text)

    # roles residuales
    text = re.sub(r"\b(system|assistant|user)\s*>", "", text, flags=re.IGNORECASE)

    # secuencias raras repetidas por plantillas de chat
    text = re.sub(r"\b(system|assistant|user)\b\s*:", "", text, flags=re.IGNORECASE)

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()

def clean_stream_chunk(text: Optional[str]) -> str:
    """
    Limpia un chunk individual recibido en streaming.
    """
    if not text:
        return ""

    if not isinstance(text, str):
        text = str(text)

    for token in STREAM_EXACT_TOKENS:
        text = text.replace(token, "")

    text = re.sub(r"<\|[^>]+\|>", "", text)
    text = re.sub(r"<[^>]+>", "", text)

    text = re.sub(
        r"(system|assistant|user)\s*>",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    return text


def _build_payload(
    messages: list[dict[str, str]],
    max_tokens: int = OLLAMA_MAX_TOKENS,
    stream: bool = False,
) -> dict:
    """
    Construye el payload estándar para Ollama.
    """
    return {
        "model": OLLAMA_CHAT_MODEL,
        "messages": messages,
        "stream": stream,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
        },
    }


def generate_response(
    messages: list[dict[str, str]],
    max_tokens: int = OLLAMA_MAX_TOKENS,
) -> str:
    """
    Envía mensajes al endpoint /api/chat de Ollama
    y devuelve el contenido textual completo de la respuesta.
    """
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = _build_payload(messages=messages, max_tokens=max_tokens, stream=False)

    try:
        logger.info("Enviando petición no-stream a Ollama con %s mensajes", len(messages))
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()

        data = response.json()
        message = data.get("message", {})
        content = message.get("content", "")

        cleaned = clean_response(content)
        logger.info("Respuesta completa recibida correctamente desde Ollama")
        return cleaned

    except requests.RequestException as exc:
        logger.exception("Fallo al comunicarse con Ollama")
        raise OllamaConnectionError(
            f"No se pudo obtener respuesta del modelo local: {exc}"
        ) from exc


def generate_response_stream(
    messages: list[dict[str, str]],
    max_tokens: int = OLLAMA_MAX_TOKENS,
) -> Generator[str, None, None]:
    """
    Envía mensajes al endpoint /api/chat de Ollama usando streaming
    y va devolviendo fragmentos de texto progresivamente.
    """
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = _build_payload(messages=messages, max_tokens=max_tokens, stream=True)

    try:
        logger.info("Enviando petición stream a Ollama con %s mensajes", len(messages))

        with requests.post(url, json=payload, timeout=180, stream=True) as response:
            response.raise_for_status()

            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue

                try:
                    data = json.loads(raw_line)
                except json.JSONDecodeError:
                    logger.warning("Línea de streaming no válida recibida de Ollama")
                    continue

                message = data.get("message", {})
                chunk = message.get("content", "")

                if chunk:
                    cleaned_chunk = clean_stream_chunk(chunk)
                    if cleaned_chunk:
                        yield cleaned_chunk

                if data.get("done", False):
                    break

        logger.info("Streaming completado correctamente desde Ollama")

    except requests.RequestException as exc:
        logger.exception("Fallo durante el streaming con Ollama")
        raise OllamaConnectionError(
            f"No se pudo obtener respuesta en streaming del modelo local: {exc}"
        ) from exc


def collect_streamed_response(
    messages: list[dict[str, str]],
    max_tokens: int = OLLAMA_MAX_TOKENS,
) -> str:
    """
    Ejecuta streaming interno y devuelve el texto final completo.
    """
    chunks = []
    for chunk in generate_response_stream(messages=messages, max_tokens=max_tokens):
        chunks.append(chunk)

    return clean_response("".join(chunks))


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


def format_tool_result_with_llm_stream(
    user_prompt: str,
    tool_name: str,
    tool_result: str,
) -> Generator[str, None, None]:
    """
    Igual que format_tool_result_with_llm, pero devolviendo chunks en streaming.
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

    yield from generate_response_stream(messages)