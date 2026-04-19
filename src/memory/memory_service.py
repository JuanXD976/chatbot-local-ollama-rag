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

def find_memory_fact_by_prefix(prefix: str) -> str | None:
    """
    Busca en la memoria persistente una entrada que empiece por un prefijo concreto.
    """
    memory = get_persistent_memory()

    for item in reversed(memory):
        content = item.get("content", "").strip()
        if content.lower().startswith(prefix.lower()):
            return content

    return None


def answer_memory_question(user_prompt: str) -> str | None:
    """
    Responde de forma determinista a preguntas simples sobre memoria.
    """
    prompt = user_prompt.strip().lower()

    if any(q in prompt for q in ["cómo me llamo", "como me llamo", "cuál es mi nombre", "cual es mi nombre"]):
        fact = find_memory_fact_by_prefix("Mi nombre es")
        if fact:
            return fact
        return "No tengo guardado tu nombre todavía."

    if any(q in prompt for q in ["dónde trabajo", "donde trabajo", "en qué trabajo", "en que trabajo"]):
        fact = find_memory_fact_by_prefix("Trabajo en")
        if fact:
            return fact
        return "No tengo guardado dónde trabajas."

    if any(q in prompt for q in ["qué me gusta", "que me gusta", "cuáles son mis gustos", "cuales son mis gustos"]):
        fact = find_memory_fact_by_prefix("Me gusta")
        if fact:
            return fact
        return "No tengo guardado qué te gusta."

    if any(q in prompt for q in ["dónde vivo", "donde vivo"]):
        fact = find_memory_fact_by_prefix("Vivo en")
        if fact:
            return fact
        return "No tengo guardado dónde vives."

    if any(q in prompt for q in ["qué estudio", "que estudio"]):
        fact = find_memory_fact_by_prefix("Estudio")
        if fact:
            return fact
        return "No tengo guardado qué estudias."

    return None