"""
Gestión de la base de datos vectorial Chroma.

Motivo de su creación:
- Centralizar la configuración del vectorstore.
- Evitar duplicar la inicialización de embeddings y Chroma.
"""

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from src.config.settings import (
    RAG_CHROMA_PATH,
    RAG_EMBEDDING_MODEL,
)


def get_embeddings_model() -> HuggingFaceEmbeddings:
    """
    Devuelve el modelo de embeddings configurado para el proyecto.
    """
    return HuggingFaceEmbeddings(model_name=RAG_EMBEDDING_MODEL)


def get_vectorstore() -> Chroma:
    """
    Devuelve la instancia persistente de Chroma.
    """
    embeddings = get_embeddings_model()

    return Chroma(
        persist_directory=RAG_CHROMA_PATH,
        embedding_function=embeddings,
    )