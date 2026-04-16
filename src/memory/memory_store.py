"""
Persistencia de memoria conversacional en JSON.

Motivo de su creación:
- Leer y escribir historial persistente del chatbot.
- Mantener aislada la lógica de acceso a disco.
"""

from __future__ import annotations

import json
from pathlib import Path


def ensure_memory_file_exists(file_path: str) -> None:
    """
    Crea el archivo de memoria si no existe.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text("[]", encoding="utf-8")


def load_memory(file_path: str) -> list[dict[str, str]]:
    """
    Carga el historial persistente desde disco.
    """
    ensure_memory_file_exists(file_path)

    path = Path(file_path)

    try:
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return []

        data = json.loads(content)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):
        return []


def save_memory(file_path: str, messages: list[dict[str, str]]) -> None:
    """
    Guarda el historial completo en disco.
    """
    ensure_memory_file_exists(file_path)

    path = Path(file_path)
    path.write_text(
        json.dumps(messages, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def clear_memory(file_path: str) -> None:
    """
    Resetea la memoria persistente.
    """
    save_memory(file_path, [])