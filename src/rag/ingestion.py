"""
Ingesta de documentos para el sistema RAG.

Motivo:
- Cargar documentos soportados.
- Trocearlos.
- Insertarlos o reindexarlos en ChromaDB.
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config.settings import (
    RAG_CHUNK_OVERLAP,
    RAG_CHUNK_SIZE,
    RAG_RAW_DATA_PATH,
    RAG_SUPPORTED_EXTENSIONS,
)
from src.rag.vectorstore import (
    add_documents_to_vectorstore,
    clear_vectorstore,
    delete_documents_by_source_name,
)


def _load_text_file_with_fallback(file_path: Path) -> list[Document]:
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]

    content = None
    last_error = None

    for encoding in encodings:
        try:
            content = file_path.read_text(encoding=encoding)
            break
        except Exception as exc:
            last_error = exc

    if content is None:
        raise RuntimeError(f"No se pudo leer el archivo de texto {file_path}: {last_error}")

    return [
        Document(
            page_content=content,
            metadata={
                "source": str(file_path),
                "source_name": file_path.name,
                "source_extension": file_path.suffix.lower(),
                "page_or_chunk": 1,
            },
        )
    ]


def _load_single_file(file_path: Path) -> list[Document]:
    suffix = file_path.suffix.lower()

    if suffix in {".txt", ".md"}:
        docs = _load_text_file_with_fallback(file_path)
    elif suffix == ".pdf":
        loader = PyPDFLoader(str(file_path))
        docs = loader.load()
    elif suffix == ".docx":
        loader = Docx2txtLoader(str(file_path))
        docs = loader.load()
    else:
        raise ValueError(f"Extensión no soportada: {suffix}")

    for index, doc in enumerate(docs, start=1):
        doc.metadata["source"] = str(file_path)
        doc.metadata["source_name"] = file_path.name
        doc.metadata["source_extension"] = suffix
        doc.metadata["page_or_chunk"] = index

    return docs


def load_documents_from_directory(directory: str) -> list[Document]:
    documents: list[Document] = []
    base_path = Path(directory)

    if not base_path.exists():
        raise FileNotFoundError(f"No existe el directorio de documentos: {directory}")

    for file_path in base_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in RAG_SUPPORTED_EXTENSIONS:
            docs = _load_single_file(file_path)
            documents.extend(docs)

    if not documents:
        raise ValueError(
            f"No se encontraron documentos soportados en {directory}. "
            f"Extensiones válidas: {RAG_SUPPORTED_EXTENSIONS}"
        )

    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
    )

    split_docs = splitter.split_documents(documents)

    per_source_counter: dict[str, int] = {}

    for doc in split_docs:
        source_name = doc.metadata.get("source_name", "unknown")
        current = per_source_counter.get(source_name, 0)
        doc.metadata["chunk_index"] = current
        per_source_counter[source_name] = current + 1

    return split_docs


def ingest_documents() -> int:
    """
    Reindexa todo el directorio raw completo.
    """
    raw_documents = load_documents_from_directory(RAG_RAW_DATA_PATH)
    split_docs = split_documents(raw_documents)

    clear_vectorstore()
    return add_documents_to_vectorstore(split_docs)


def ingest_single_file(file_path: str | Path) -> int:
    """
    Indexa o reindexa un único documento.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    documents = _load_single_file(path)
    split_docs = split_documents(documents)

    delete_documents_by_source_name(path.name)
    return add_documents_to_vectorstore(split_docs)


def remove_file_from_index(filename: str) -> int:
    """
    Elimina del índice todos los chunks asociados al archivo.
    """
    return delete_documents_by_source_name(filename)


if __name__ == "__main__":
    total_chunks = ingest_documents()
    print(f"Ingesta completada correctamente. Chunks indexados: {total_chunks}")