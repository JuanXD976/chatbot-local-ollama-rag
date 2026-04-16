"""
Configuración global del proyecto.

Motivo de su creación:
- Centralizar parámetros importantes.
- Evitar valores fijos repartidos por el código.
- Facilitar cambios futuros sin tocar varios archivos.
"""
from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()


# =========================
# APP
# =========================
APP_TITLE = "🤖 Chatbot Local con Ollama - V1.4"
APP_DESCRIPTION = (
    "Versión modular del chatbot local con Streamlit, Ollama, tools, RAG, memoria, sesiones y streaming en tiempo real."
)
MAX_MESSAGES = 6
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# =========================
# OLLAMA
# =========================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "gemma3:4")
OLLAMA_MAX_TOKENS = int(os.getenv("OLLAMA_MAX_TOKENS", "1200"))

# =========================
# WEB SEARCH
# =========================
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# =========================
# RAG
# =========================
RAG_RAW_DATA_PATH = "data/raw"
RAG_CHROMA_PATH = "data/vectorstore/chroma_db"
RAG_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

"""
RAG_CHUNK_SIZE

Es el tamaño aproximado de cada fragmento.

Ejemplo:

si el texto es largo, se corta en trozos de unas 800 unidades de texto

RAG_CHUNK_OVERLAP

Es el solapamiento entre chunks.

Ejemplo:

chunk 1 termina en una frase
chunk 2 repite un poco del final del chunk 1

Esto ayuda a no perder contexto en cortes bruscos.

RAG_TOP_K = 4

Significa:

cuando haces una consulta, el retriever recupera los 4 chunks más relevantes
"""

RAG_CHUNK_SIZE = 800
RAG_CHUNK_OVERLAP = 150
RAG_TOP_K = 4

# =========================
# MEMORY
# =========================
MEMORY_FILE_PATH = "data/memory/conversation_history.json"
MEMORY_MAX_MESSAGES = 100

# =========================
# SESSIONS
# =========================
SESSION_FILE_PATH = "data/memory/chat_sessions.json"