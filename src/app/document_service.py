"""
Servicio de gestión documental.

Motivo:
- Gestionar subida de archivos.
- Gestionar reconstrucción del RAG.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from src.config.settings import RAG_CHROMA_PATH, RAG_RAW_DATA_PATH
from src.rag.ingestion import ingest_documents


class DocumentService:
    @staticmethod
    def save_uploaded_file(uploaded_file) -> str:
        """
        Guarda un archivo subido en data/raw.
        """
        raw_path = Path(RAG_RAW_DATA_PATH)
        raw_path.mkdir(parents=True, exist_ok=True)

        save_path = raw_path / uploaded_file.name

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return str(save_path)

    @staticmethod
    def rebuild_vectorstore() -> int:
        """
        Reconstruye la base vectorial desde cero para evitar duplicados.
        """
        chroma_path = Path(RAG_CHROMA_PATH)

        if chroma_path.exists():
            shutil.rmtree(chroma_path)

        return ingest_documents()