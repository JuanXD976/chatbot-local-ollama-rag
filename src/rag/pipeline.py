"""
Pipeline RAG del proyecto.

Motivo de su creación:
- Recuperar contexto relevante.
- Construir un prompt enriquecido.
- Generar respuesta con el LLM local.
"""

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
                "usando únicamente el contexto recuperado de una base de conocimiento local. "
                "Responde siempre en español. "
                "No inventes información. "
                "Si el contexto no contiene la respuesta exacta, dilo claramente. "
                "Cuando sea útil, menciona que la respuesta se basa en la base de conocimiento local."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Pregunta del usuario:\n{user_prompt}\n\n"
                f"Contexto recuperado:\n{context}\n\n"
                "Responde de forma clara, útil y basándote solo en el contexto recuperado."
            ),
        },
    ]

    return generate_response(messages)