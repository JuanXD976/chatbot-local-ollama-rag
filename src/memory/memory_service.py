"""
Servicio de memoria conversacional.

Motivo de su creación:
- Orquestar lectura, escritura y reseteo de la memoria persistente.
- Encapsular la lógica de negocio relacionada con la memoria.
"""

from __future__ import annotations

import re

from src.config.settings import MEMORY_FILE_PATH, MEMORY_MAX_MESSAGES
from src.memory.memory_store import clear_memory, load_memory, save_memory

def _normalize_text(text: str) -> str:
    """
    Normaliza texto para comparar duplicados de forma simple.
    """
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text

def _message_already_exists(messages: list[dict[str, str]], content: str) -> bool:
    """
    Comprueba si un mensaje de usuario ya existe en memoria persistente.
    """
    normalized_new = _normalize_text(content)

    for msg in messages:
        if msg.get("role") != "user":
            continue

        normalized_existing = _normalize_text(msg.get("content", ""))
        if normalized_existing == normalized_new:
            return True

    return False

def get_persistent_memory() -> list[dict[str, str]]:
    """
    Devuelve la memoria persistente actual.
    """
    return load_memory(MEMORY_FILE_PATH)


def append_message_to_memory(role: str, content: str) -> None:
    """
    Añade un mensaje nuevo a la memoria persistente evitando duplicados exactos.
    """
    if not content or not content.strip():
        return

    messages = load_memory(MEMORY_FILE_PATH)

    # Evitar duplicados exactos solo para mensajes del usuario
    if role == "user" and _message_already_exists(messages, content):
        return

    messages.append({"role": role, "content": content})

    if len(messages) > MEMORY_MAX_MESSAGES:
        messages = messages[-MEMORY_MAX_MESSAGES:]

    save_memory(MEMORY_FILE_PATH, messages)


def replace_memory(messages: list[dict[str, str]]) -> None:
    """
    Sustituye completamente la memoria persistente.
    """
    trimmed_messages = messages[-MEMORY_MAX_MESSAGES:]
    save_memory(MEMORY_FILE_PATH, trimmed_messages)


def reset_persistent_memory() -> None:
    """
    Borra toda la memoria persistente.
    """
    clear_memory(MEMORY_FILE_PATH)