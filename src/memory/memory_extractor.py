"""
Extracción simple de memoria útil del usuario.

Motivo:
- Guardar solo hechos relevantes.
- Evitar contaminar la memoria con prompts temporales.
"""

from __future__ import annotations

import re


def _clean_value(value: str) -> str:
    cleaned = value.strip(" .,:;!?¿¡\"'")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def extract_memory_fact(user_prompt: str) -> str | None:
    """
    Extrae un hecho útil si el mensaje parece memoria persistente.
    Devuelve una frase limpia o None.
    """
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
            r"\bmi empresa es\s+(.+)$",
            lambda v: f"Mi empresa es {_clean_value(v)}."
        ),
        (
            r"\bvivo en\s+(.+)$",
            lambda v: f"Vivo en {_clean_value(v)}."
        ),
        (
            r"\bestudio\s+(.+)$",
            lambda v: f"Estudio {_clean_value(v)}."
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

    prompt_lower = text.lower()

    for pattern, builder in patterns:
        match = re.search(pattern, prompt_lower, re.IGNORECASE)
        if match:
            raw_value = text[match.start(1):match.end(1)]
            cleaned = _clean_value(raw_value)
            if cleaned:
                return builder(cleaned)

    return None