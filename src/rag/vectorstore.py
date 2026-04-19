"""
Gestión del vectorstore Chroma.

Motivo:
- Centralizar la conexión con ChromaDB.
- Reutilizar embeddings y vectorstore persistente.
- Permitir inserción, borrado y reindexación sin tocar la carpeta física.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from src.config.settings import (
    RAG_CHROMA_PATH,
    RAG_EMBEDDING_MODEL,
)

_embeddings = None
_vectorstore = None


def get_embeddings():
    global _embeddings

    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=RAG_EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
        )

    return _embeddings


def get_vectorstore() -> Chroma:
    global _vectorstore

    if _vectorstore is None:
        Path(RAG_CHROMA_PATH).mkdir(parents=True, exist_ok=True)

        _vectorstore = Chroma(
            persist_directory=RAG_CHROMA_PATH,
            embedding_function=get_embeddings(),
            collection_name="chatbot_local_docs",
        )

    return _vectorstore


def build_chunk_id(source_name: str, page_or_chunk: int, chunk_index: int, content: str) -> str:
    """
    Genera un id estable por fragmento para poder borrar/reinsertar fácilmente.
    """
    digest = hashlib.md5(content.encode("utf-8")).hexdigest()[:12]
    return f"{source_name}::p{page_or_chunk}::c{chunk_index}::{digest}"


def add_documents_to_vectorstore(documents) -> int:
    """
    Inserta una lista de documentos ya troceados en Chroma.
    """
    if not documents:
        return 0

    vectorstore = get_vectorstore()

    ids = []
    for doc in documents:
        source_name = doc.metadata.get("source_name", "unknown")
        page_or_chunk = int(doc.metadata.get("page_or_chunk", 0))
        chunk_index = int(doc.metadata.get("chunk_index", 0))
        content = doc.page_content or ""

        chunk_id = build_chunk_id(
            source_name=source_name,
            page_or_chunk=page_or_chunk,
            chunk_index=chunk_index,
            content=content,
        )
        ids.append(chunk_id)

    vectorstore.add_documents(documents=documents, ids=ids)
    return len(ids)


def get_ids_by_source_name(source_name: str) -> list[str]:
    """
    Recupera ids de todos los chunks asociados a un documento.
    """
    vectorstore = get_vectorstore()
    result = vectorstore._collection.get(
        where={"source_name": source_name},
        include=[],
    )
    return result.get("ids", []) if result else []


def delete_documents_by_source_name(source_name: str) -> int:
    """
    Elimina del índice todos los chunks asociados a un documento.
    """
    vectorstore = get_vectorstore()
    ids = get_ids_by_source_name(source_name)

    if not ids:
        return 0

    vectorstore._collection.delete(ids=ids)
    return len(ids)


def clear_vectorstore() -> int:
    """
    Elimina todos los documentos indexados de la colección actual.
    """
    vectorstore = get_vectorstore()
    result = vectorstore._collection.get(include=[])
    ids = result.get("ids", []) if result else []

    if not ids:
        return 0

    vectorstore._collection.delete(ids=ids)
    return len(ids)


def count_indexed_chunks() -> int:
    """
    Devuelve el número total de chunks indexados.
    """
    vectorstore = get_vectorstore()
    result = vectorstore._collection.get(include=[])
    ids = result.get("ids", []) if result else []
    return len(ids)