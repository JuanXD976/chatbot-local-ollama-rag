"""
Servicio de gestión documental.

Motivo:
- Guardar archivos.
- Listarlos.
- Eliminarlos.
- Indexarlos automáticamente.
- Reindexar el corpus completo cuando sea necesario.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.config.settings import (
    RAG_RAW_DATA_PATH,
    RAG_SUPPORTED_EXTENSIONS,
)
from src.rag.ingestion import ingest_documents, ingest_single_file, remove_file_from_index
from src.rag.vectorstore import count_indexed_chunks


class DocumentService:
    @staticmethod
    def _raw_path() -> Path:
        raw_path = Path(RAG_RAW_DATA_PATH)
        raw_path.mkdir(parents=True, exist_ok=True)
        return raw_path

    @staticmethod
    def list_documents() -> list[dict]:
        raw_path = DocumentService._raw_path()

        documents = []
        for file_path in sorted(raw_path.iterdir(), key=lambda p: p.name.lower()):
            if file_path.is_file() and file_path.suffix.lower() in RAG_SUPPORTED_EXTENSIONS:
                stat = file_path.stat()
                documents.append(
                    {
                        "name": file_path.name,
                        "path": str(file_path),
                        "size_bytes": stat.st_size,
                        "suffix": file_path.suffix.lower(),
                        "modified_at": datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M"),
                    }
                )

        return documents

    @staticmethod
    def count_documents() -> int:
        return len(DocumentService.list_documents())

    @staticmethod
    def _resolve_safe_destination(filename: str) -> Path:
        raw_path = DocumentService._raw_path()

        safe_name = Path(filename).name
        suffix = Path(safe_name).suffix.lower()

        if suffix not in RAG_SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Extensión no soportada: {suffix}. "
                f"Formatos válidos: {', '.join(RAG_SUPPORTED_EXTENSIONS)}"
            )

        candidate_path = raw_path / safe_name

        if candidate_path.exists():
            stem = candidate_path.stem
            counter = 1

            while True:
                new_name = f"{stem}_{counter}{suffix}"
                new_path = raw_path / new_name
                if not new_path.exists():
                    candidate_path = new_path
                    break
                counter += 1

        return candidate_path

    @staticmethod
    def save_file_bytes(filename: str, content: bytes) -> tuple[str, int]:
        """
        Guarda un archivo y lo indexa automáticamente.
        Si la indexación falla, revierte guardado.
        """
        destination = DocumentService._resolve_safe_destination(filename)

        with open(destination, "wb") as f:
            f.write(content)

        try:
            indexed_chunks = ingest_single_file(destination)
            return str(destination), indexed_chunks
        except Exception:
            if destination.exists():
                destination.unlink()
            raise

    @staticmethod
    def save_uploaded_file(uploaded_file) -> tuple[str, int]:
        return DocumentService.save_file_bytes(uploaded_file.name, uploaded_file.getbuffer())

    @staticmethod
    def delete_document(filename: str) -> dict:
        safe_name = Path(filename).name
        file_path = DocumentService._raw_path() / safe_name

        if not file_path.exists() or not file_path.is_file():
            return {"deleted_file": False, "deleted_chunks": 0}

        deleted_chunks = remove_file_from_index(safe_name)
        file_path.unlink()

        return {
            "deleted_file": True,
            "deleted_chunks": deleted_chunks,
        }

    @staticmethod
    def rebuild_vectorstore() -> int:
        documents = DocumentService.list_documents()
        if not documents:
            raise ValueError("No hay documentos disponibles para indexar.")

        return ingest_documents()

    @staticmethod
    def get_rag_status() -> dict:
        document_count = DocumentService.count_documents()
        indexed_chunks = count_indexed_chunks()

        return {
            "document_count": document_count,
            "indexed_chunks": indexed_chunks,
            "vectorstore_exists": indexed_chunks > 0,
            "supported_extensions": list(RAG_SUPPORTED_EXTENSIONS),
        }