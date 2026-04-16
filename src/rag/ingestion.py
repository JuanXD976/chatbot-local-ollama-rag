"""
Ingesta de documentos para el sistema RAG.

Motivo de su creación:
- Leer documentos locales.
- Dividirlos en fragmentos.
- Vectorizarlos.
- Almacenarlos en Chroma.
"""

from pathlib import Path

from annotated_types import doc
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config.settings import (
    RAG_CHUNK_OVERLAP,
    RAG_CHUNK_SIZE,
    RAG_RAW_DATA_PATH,
)
from src.rag.vectorstore import get_vectorstore


SUPPORTED_EXTENSIONS = {".txt", ".md"}


def load_documents_from_directory(directory: str) -> list[Document]:
    """
    Carga todos los documentos soportados desde un directorio.
    """
    documents: list[Document] = []
    base_path = Path(directory)

    if not base_path.exists():
        raise FileNotFoundError(f"No existe el directorio de documentos: {directory}")

    for file_path in base_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            loader = TextLoader(str(file_path), encoding="utf-8")
            docs = loader.load()

            for doc in docs:
                doc.metadata["source"] = str(file_path)
                doc.metadata["source_name"] = file_path.name

            documents.extend(docs)

    if not documents:
        raise ValueError(
            f"No se encontraron documentos soportados en {directory}. "
            f"Extensiones válidas: {SUPPORTED_EXTENSIONS}"
        )

    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Divide los documentos en chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
    )
    return splitter.split_documents(documents)


def ingest_documents() -> int:
    """
    Ejecuta el proceso completo de ingesta y devuelve el número de chunks indexados.
    """
    raw_documents = load_documents_from_directory(RAG_RAW_DATA_PATH)
    split_docs = split_documents(raw_documents)

    vectorstore = get_vectorstore()
    vectorstore.add_documents(split_docs)

    return len(split_docs)


if __name__ == "__main__":
    total_chunks = ingest_documents()
    print(f"Ingesta completada correctamente. Chunks indexados: {total_chunks}")