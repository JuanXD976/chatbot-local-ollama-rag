"""
Extracción segura de memoria útil del usuario.

Motivo:
- Guardar solo hechos explícitos.
- Evitar inferencias agresivas o inventadas.
"""

from __future__ import annotations

import re


def _clean_value(value: str) -> str:
    cleaned = value.strip(" .,:;!?¿¡\"'")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def extract_memory_fact(user_prompt: str) -> str | None:
    text = user_prompt.strip()

    if not text:
        return None

    patterns = [
        (
            r"\b(?:me llamo|mi nombre es)\s+(.+)$",
            lambda v: f"Mi nombre es {_clean_value(v)}."
        ),
        (
            r"\btrabajo en\s+(.+)$",
            lambda v: f"Trabajo en {_clean_value(v)}."
        ),
        (
            r"\bestudio\s+(.+)$",
            lambda v: f"Estudio {_clean_value(v)}."
        ),
        (
            r"\bvivo en\s+(.+)$",
            lambda v: f"Vivo en {_clean_value(v)}."
        ),
        (
            r"\bme gusta\s+(.+)$",
            lambda v: f"Me gusta {_clean_value(v)}."
        ),
        (
            r"\bprefiero\s+(.+)$",
            lambda v: f"Prefiero {_clean_value(v)}."
        ),
        (
            r"\bmi color favorito es\s+(.+)$",
            lambda v: f"Mi color favorito es {_clean_value(v)}."
        ),
        (
            r"\brecuerda que\s+(.+)$",
            lambda v: _clean_value(v[:1].upper() + v[1:]) + "."
        ),
    ]

    for pattern, builder in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            cleaned = _clean_value(match.group(1))
            if cleaned and len(cleaned) <= 180:
                return builder(cleaned)

    return None