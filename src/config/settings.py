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
from pathlib import Path

load_dotenv()


# =========================
# APP
# =========================
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"
MEMORY_DIR = DATA_DIR / "memory"

RAW_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

APP_TITLE = "Chatbot Local con Ollama - V8 Final"
APP_DESCRIPTION = (
    "Chatbot local multimodal con RAG persistente, modos inteligentes, adjuntos, visión y exportación."
)
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", "14"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# =========================
# OLLAMA - Models
# =========================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "gemma3:4b")
OLLAMA_VISION_MODEL=os.getenv("OLLAMA_VISION_MODEL", "gemma3:4b")
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
RAG_CHUNK_SIZE = 800
RAG_CHUNK_OVERLAP = 150
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "8"))
RAG_FINAL_K = int(os.getenv("RAG_FINAL_K", "4"))
RAG_MIN_CHARS = int(os.getenv("RAG_MIN_CHARS", "80"))
RAG_SUPPORTED_EXTENSIONS = (".txt", ".md", ".pdf", ".docx")

# =========================
# MEMORY
# =========================
MEMORY_FILE_PATH = "data/memory/conversation_history.json"
MEMORY_MAX_MESSAGES = 100

# =========================
# SESSIONS
# =========================
SESSION_FILE_PATH = str(MEMORY_DIR / "chat_sessions.json")
CONVERSATION_HISTORY_PATH = str(MEMORY_DIR / "conversation_history.json")
CHROMA_DB_DIR = str(VECTORSTORE_DIR / "chroma_db")