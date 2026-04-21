"""
Post-procesado y validación básica de respuestas.

Motivo:
- Eliminar restos peligrosos o internos del modelo.
- Reducir riesgo de fuga de contexto técnico.
"""

from __future__ import annotations

import re


FORBIDDEN_RESPONSE_PATTERNS = [
    r"system prompt",
    r"developer prompt",
    r"mensaje del sistema",
    r"instrucciones internas",
    r"contexto oculto",
]


def sanitize_final_response(text: str) -> str:
    if not text:
        return ""

    cleaned = text.strip()

    cleaned = re.sub(r"<\|[^>]+\|>", "", cleaned)
    cleaned = re.sub(r"<[a-zA-Z0-9_\-/| ]+>", "", cleaned)
    cleaned = re.sub(r"\b(system|assistant|user|chatbot)\s*:", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(system|assistant|user|chatbot)\s*>", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(system_user|assistant_user|systeme_user)\b", "", cleaned, flags=re.IGNORECASE)
    
    # Quitar prefijos técnicos no deseados al inicio
    cleaned = re.sub(r"^\s*Formato:\s*(tabla|puntos|codigo|normal)\s*\n?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^\s*Modo:\s*(auto|analista|programador|resumidor)\s*\n?", "", cleaned, flags=re.IGNORECASE)

    # Quitar tokens raros residuales
    cleaned = re.sub(r"<\|.*?\|>", "", cleaned)
    cleaned = re.sub(r"<im_.*?>", "", cleaned)
    cleaned = re.sub(r"<file_separator>", "", cleaned, flags=re.IGNORECASE)
    
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\b(Tienes nombre.*)\b", "", cleaned)
    
    return cleaned.strip()


def response_looks_sensitive(text: str) -> bool:
    lowered = (text or "").lower()

    for pattern in FORBIDDEN_RESPONSE_PATTERNS:
        if re.search(pattern, lowered, re.IGNORECASE):
            return True

    return False


def get_safe_fallback_response() -> str:
    return (
        "He descartado la respuesta generada porque parecía contener "
        "contenido interno o no adecuado. Reformula tu consulta y lo intento de nuevo."
    )