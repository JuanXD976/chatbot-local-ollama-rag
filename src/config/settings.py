"""
Configuración global del proyecto.

Motivo de su creación:
- Centralizar parámetros importantes.
- Evitar valores fijos repartidos por el código.
- Facilitar cambios futuros sin tocar varios archivos.
"""

import os
from dotenv import load_dotenv

load_dotenv()


OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_CHAT_MODEL = "gemma3:4"
APP_TITLE = "🤖 Chatbot V1 Local con Ollama"
APP_DESCRIPTION = "Primera versión del chatbot local usando Streamlit y Ollama."
MAX_MESSAGES = 6
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

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

RAG_CHUNK_SIZE = int(800)
RAG_CHUNK_OVERLAP = int(150)
RAG_TOP_K = int(4)