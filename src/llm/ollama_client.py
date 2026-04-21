"""
Cliente para conectarse a la API local de Ollama.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Generator, Optional

import requests

from src.config.settings import OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL, OLLAMA_MAX_TOKENS
from src.core.exceptions import OllamaConnectionError
from src.core.system_prompt import build_base_system_prompt
from src.utils.language import detect_language

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
    "<|im_start|>",
    "<|im_end|>",
    "<|start_header_id|>",
    "<|end_header_id|>",
    "<|eot_id|>",
    "system>",
    "assistant>",
    "user>",
    "chatbot>",
    "system_user",
    "assistant_user",
    "systeme_user",
]


def check_ollama_connection() -> dict:
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
    if not text:
        return ""

    if not isinstance(text, str):
        text = str(text)

    for token in STREAM_EXACT_TOKENS:
        text = text.replace(token, "")

    text = re.sub(r"<\|[^>]+\|>", "", text)
    text = re.sub(r"<[a-zA-Z0-9_\-/| ]+>", "", text)
    text = re.sub(r"\bim_[a-zA-Z_ ]+\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(system|assistant|user|chatbot)\s*:", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(system|assistant|user|chatbot)\s*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?mi)^\s*(system_user|assistant_user|systeme_user)\s*$", "", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def clean_stream_chunk(text: Optional[str]) -> str:
    if not text:
        return ""

    if not isinstance(text, str):
        text = str(text)

    for token in STREAM_EXACT_TOKENS:
        text = text.replace(token, "")

    text = re.sub(r"<\|[^>]+\|>", "", text)
    text = re.sub(r"<[a-zA-Z0-9_\-/| ]+>", "", text)
    text = re.sub(r"\bim_[a-zA-Z_ ]+\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(system|assistant|user|chatbot)\s*:", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(system|assistant|user|chatbot)\s*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(system_user|assistant_user|systeme_user)\b", "", text, flags=re.IGNORECASE)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    return text


def _build_payload(
    messages: list[dict[str, str]],
    max_tokens: int = OLLAMA_MAX_TOKENS,
    stream: bool = False,
) -> dict:
    return {
        "model": OLLAMA_CHAT_MODEL,
        "messages": messages,
        "stream": stream,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.4,
            "top_p": 0.9,
            "repeat_penalty": 1.15,
            "stop": [
                "<|im_start|>",
                "<|im_end|>",
                "<|start_header_id|>",
                "<|end_header_id|>",
                "<|eot_id|>",
                "assistant>",
                "user>",
                "system>",
                "chatbot>",
                "system_user",
                "assistant_user",
                "systeme_user",
            ],
        },
    }


def generate_response(
    messages: list[dict[str, str]],
    max_tokens: int = OLLAMA_MAX_TOKENS,
) -> str:
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = _build_payload(messages=messages, max_tokens=max_tokens, stream=False)

    try:
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()
        message = data.get("message", {})
        content = message.get("content", "")
        return clean_response(content)

    except requests.RequestException as exc:
        raise OllamaConnectionError(
            f"No se pudo obtener respuesta del modelo local: {exc}"
        ) from exc


def generate_response_stream(
    messages: list[dict[str, str]],
    max_tokens: int = OLLAMA_MAX_TOKENS,
) -> Generator[str, None, None]:
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = _build_payload(messages=messages, max_tokens=max_tokens, stream=True)

    try:
        with requests.post(url, json=payload, timeout=180, stream=True) as response:
            response.raise_for_status()

            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue

                try:
                    data = json.loads(raw_line)
                except json.JSONDecodeError:
                    continue

                message = data.get("message", {})
                chunk = message.get("content", "")

                if chunk:
                    cleaned_chunk = clean_stream_chunk(chunk)
                    if cleaned_chunk:
                        yield cleaned_chunk

                if data.get("done", False):
                    break

    except requests.RequestException as exc:
        raise OllamaConnectionError(
            f"No se pudo obtener respuesta en streaming del modelo local: {exc}"
        ) from exc


def format_tool_result_with_llm(user_prompt: str, tool_name: str, tool_result: str) -> str:
    language = detect_language(user_prompt)

    messages = [
        {
            "role": "system",
            "content": (
                build_base_system_prompt(language)
                + "Your task is to transform tool outputs into a final, natural and useful response. "
                + "Do not invent data. "
                + "Do not mention internal names like tool, router or API."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Original user request: {user_prompt}\n\n"
                f"Tool used: {tool_name}\n\n"
                f"Tool result:\n{tool_result}\n\n"
                "Write the final user-facing answer."
            ),
        },
    ]

    return generate_response(messages)


def format_tool_result_with_llm_stream(
    user_prompt: str,
    tool_name: str,
    tool_result: str,
):
    language = detect_language(user_prompt)

    messages = [
        {
            "role": "system",
            "content": (
                build_base_system_prompt(language)
                + "Transform tool outputs into a final, clear and useful response. "
                + "Do not invent data."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Original user request: {user_prompt}\n\n"
                f"Tool used: {tool_name}\n\n"
                f"Tool result:\n{tool_result}\n\n"
                "Write the final user-facing answer."
            ),
        },
    ]

    yield from generate_response_stream(messages)