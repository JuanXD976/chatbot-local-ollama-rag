"""
Servicio de gestión documental.

Motivo:
- Gestionar subida de archivos.
- Listar documentos disponibles.
- Eliminar documentos.
- Reconstruir la base vectorial del RAG.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from src.config.settings import (
    RAG_CHROMA_PATH,
    RAG_RAW_DATA_PATH,
    RAG_SUPPORTED_EXTENSIONS,
)
from src.rag.ingestion import ingest_documents


class DocumentService:
    @staticmethod
    def _raw_path() -> Path:
        raw_path = Path(RAG_RAW_DATA_PATH)
        raw_path.mkdir(parents=True, exist_ok=True)
        return raw_path

    @staticmethod
    def _vectorstore_path() -> Path:
        return Path(RAG_CHROMA_PATH)

    @staticmethod
    def list_documents() -> list[dict]:
        """
        Lista los documentos disponibles en data/raw.
        """
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
    def save_uploaded_file(uploaded_file) -> str:
        """
        Guarda un archivo subido en data/raw evitando sobreescritura accidental.
        Si ya existe, crea un nombre incremental.
        """
        raw_path = DocumentService._raw_path()

        original_name = Path(uploaded_file.name).name
        suffix = Path(original_name).suffix.lower()

        if suffix not in RAG_SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Extensión no soportada: {suffix}. "
                f"Formatos válidos: {', '.join(RAG_SUPPORTED_EXTENSIONS)}"
            )

        candidate_path = raw_path / original_name

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

        with open(candidate_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return str(candidate_path)

    @staticmethod
    def delete_document(filename: str) -> bool:
        """
        Elimina un documento concreto de data/raw.
        """
        safe_name = Path(filename).name
        file_path = DocumentService._raw_path() / safe_name

        if not file_path.exists() or not file_path.is_file():
            return False

        file_path.unlink()
        return True

    @staticmethod
    def rebuild_vectorstore() -> int:
        """
        Reconstruye la base vectorial desde cero para evitar duplicados.
        """
        documents = DocumentService.list_documents()
        if not documents:
            raise ValueError("No hay documentos disponibles para indexar.")

        chroma_path = DocumentService._vectorstore_path()

        if chroma_path.exists():
            try:
                shutil.rmtree(chroma_path)
            except Exception as exc:
                raise RuntimeError(
                    "No se puede reconstruir ahora mismo porque la base vectorial está en uso.\n"
                    "Solución: reinicia la aplicación y vuelve a intentarlo."
                ) from exc

        return ingest_documents()

    @staticmethod
    def get_rag_status() -> dict:
        """
        Devuelve un estado simple del módulo documental/RAG.
        """
        document_count = DocumentService.count_documents()
        vectorstore_exists = DocumentService._vectorstore_path().exists()

        return {
            "document_count": document_count,
            "vectorstore_exists": vectorstore_exists and document_count > 0,
            "supported_extensions": list(RAG_SUPPORTED_EXTENSIONS),
        }