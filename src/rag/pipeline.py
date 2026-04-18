"""
Pipeline RAG del proyecto.

Motivo de su creación:
- Recuperar contexto relevante.
- Construir un prompt enriquecido.
- Generar respuesta con el LLM local.
"""

from __future__ import annotations

from typing import Generator

from src.llm.ollama_client import generate_response, generate_response_stream
from src.rag.retriever import format_retrieved_context, retrieve_documents


def build_rag_messages(user_prompt: str) -> list[dict[str, str]] | None:
    """
    Construye los mensajes para responder usando RAG.
    """
    retrieved_docs = retrieve_documents(user_prompt)
    context = format_retrieved_context(retrieved_docs)

    if not context:
        return None

    messages = [
        {
            "role": "system",
            "content": (
                "Eres un asistente preciso y profesional especializado en responder "
                "usando únicamente información recuperada de una base de conocimiento local. "
                "Responde siempre en español. "
                "No inventes información. "
                "Si la información no aparece en el contexto, dilo claramente. "
                "Redacta la respuesta de forma natural y útil para el usuario. "
                "No menciones rutas de archivos, nombres de carpetas, fragmentos, chunks, "
                "metadatos técnicos ni expresiones como 'contexto recuperado'. "
                "No copies encabezados técnicos. "
                "Integra la información de forma fluida, como una respuesta normal. "
                "Solo menciona el nombre del archivo si aporta valor real a la respuesta."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Pregunta del usuario:\n{user_prompt}\n\n"
                f"Información disponible:\n{context}\n\n"
                "Responde basándote solo en esa información."
            ),
        },
    ]

    return messages


def answer_with_rag(user_prompt: str) -> str:
    """
    Responde a una consulta usando recuperación de contexto local + generación con el LLM.
    """
    messages = build_rag_messages(user_prompt)

    if not messages:
        return (
            "No he encontrado información relevante en la base de conocimiento local "
            "para responder a tu consulta."
        )

    return generate_response(messages)


def answer_with_rag_stream(user_prompt: str) -> Generator[str, None, None]:
    """
    Variante streaming del pipeline RAG.
    """
    messages = build_rag_messages(user_prompt)

    if not messages:
        yield (
            "No he encontrado información relevante en la base de conocimiento local "
            "para responder a tu consulta."
        )
        return

    yield from generate_response_stream(messages)