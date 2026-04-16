"""
Pipeline RAG del proyecto.

Motivo de su creación:
- Recuperar contexto relevante.
- Construir un prompt enriquecido.
- Generar respuesta con el LLM local.
"""

from __future__ import annotations

from src.llm.ollama_client import generate_response
from src.rag.retriever import format_retrieved_context, retrieve_documents


def answer_with_rag(user_prompt: str) -> str:
    """
    Responde a una consulta usando recuperación de contexto local + generación con el LLM.
    """
    retrieved_docs = retrieve_documents(user_prompt)
    context = format_retrieved_context(retrieved_docs)

    if not context:
        return (
            "No he encontrado información relevante en la base de conocimiento local "
            "para responder a tu consulta."
        )

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

    return generate_response(messages)