"""
Retriever para el sistema RAG.

Motivo de su creación:
- Encapsular la recuperación semántica de contexto.
- Permitir reutilización desde router, tools o pipeline.
"""

from langchain_core.documents import Document

from src.config.settings import RAG_TOP_K
from src.rag.vectorstore import get_vectorstore


def get_retriever():
    """
    Devuelve un retriever de Chroma configurado con el número de resultados deseado.
    """
    vectorstore = get_vectorstore()

    return vectorstore.as_retriever(
        search_kwargs={"k": RAG_TOP_K}
    )


def retrieve_documents(query: str) -> list[Document]:
    """
    Recupera los documentos más relevantes para una consulta.
    """
    retriever = get_retriever()
    return retriever.invoke(query)


def format_retrieved_context(documents: list[Document]) -> str:
    """
    Convierte los documentos recuperados en un bloque de contexto legible para el LLM.
    """
    if not documents:
        return ""

    formatted_chunks = []

    for index, doc in enumerate(documents, start=1):
        source = doc.metadata.get("source", "fuente_desconocida")
        content = doc.page_content.strip()

        formatted_chunks.append(
            f"[Fragmento {index} | Fuente: {source}]\n{content}"
        )

    return "\n\n".join(formatted_chunks)