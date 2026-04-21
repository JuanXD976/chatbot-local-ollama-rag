"""
Retriever para el sistema RAG.

Motivo de su creación:
- Encapsular la recuperación semántica de contexto.
- Permitir reutilización desde router, tools o pipeline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.config.settings import RAG_FINAL_K, RAG_MIN_CHARS, RAG_TOP_K
from src.rag.vectorstore import count_indexed_chunks, get_vectorstore


@dataclass
class RetrievedChunk:
    text: str
    source_name: str
    score: float


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9_]+", (text or "").lower())


def _keyword_score(query: str, text: str) -> float:
    q_tokens = set(_tokenize(query))
    d_tokens = _tokenize(text)

    if not q_tokens or not d_tokens:
        return 0.0

    overlap = sum(1 for token in d_tokens if token in q_tokens)
    uniq_overlap = len(q_tokens.intersection(set(d_tokens)))
    density = overlap / max(len(d_tokens), 1)

    return (uniq_overlap * 2.0) + (overlap * 0.12) + (density * 20.0)


def retrieve_hybrid_chunks(query: str) -> list[RetrievedChunk]:
    if count_indexed_chunks() == 0:
        return []

    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search_with_score(query, k=RAG_TOP_K)

    ranked: list[RetrievedChunk] = []

    for item in docs:
        if not isinstance(item, tuple) or len(item) != 2:
            continue

        doc, vector_score = item
        content = (doc.page_content or "").strip()

        if len(content) < RAG_MIN_CHARS:
            continue

        source_name = doc.metadata.get("source_name", "documento_desconocido")
        normalized_vector = 1 / (1 + float(vector_score)) if vector_score is not None else 0.0
        keyword = _keyword_score(query, content)

        final_score = (normalized_vector * 5.0) + keyword

        ranked.append(
            RetrievedChunk(
                text=content,
                source_name=source_name,
                score=final_score,
            )
        )

    ranked.sort(key=lambda x: x.score, reverse=True)
    return ranked[:RAG_FINAL_K]