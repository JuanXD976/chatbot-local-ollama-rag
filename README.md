# 🤖 Chatbot V1 Local con Ollama

Primera versión de un chatbot local desarrollado en Python utilizando **Streamlit**, **Ollama**, **tools externas** y **RAG local con ChromaDB**.

El objetivo del proyecto es construir una arquitectura modular de chatbot profesional capaz de combinar:

- generación conversacional con LLM local,
- herramientas externas (tools),
- recuperación de información mediante RAG,
- y una interfaz visual sencilla para pruebas y evolución futura.

---

# 🚀 Funcionalidades actuales

Actualmente el chatbot incorpora las siguientes capacidades:

### 💬 Chat conversacional local
- Generación de respuestas mediante modelo LLM local ejecutado en Ollama.
- Gestión de historial conversacional.
- Prompt de sistema configurable.

---

### 🌐 Búsqueda web en tiempo real
- Integración con Tavily Search API.
- Capacidad para buscar información actualizada en internet.
- Reformateo de resultados mediante LLM.

---

### 🌦 Consulta meteorológica
- Consulta meteorológica actual.
- Predicción semanal.
- Predicción próxima semana.
- Predicción fin de semana.

---

### 🕒 Fecha y hora inteligente
- Consulta de fecha/hora local.
- Consulta de hora por ubicación:
  - Ejemplo: *"¿Qué hora es en China?"*

---

### 🧮 Calculadora integrada
- Resolución de operaciones matemáticas seguras.
- Soporte para operaciones básicas:
  - suma
  - resta
  - multiplicación
  - división
  - sqrt
  - log

---

### 📚 RAG local con ChromaDB
- Base vectorial local mediante Chroma.
- Embeddings con SentenceTransformers.
- Recuperación contextual sobre documentos propios.
- Consulta sobre base documental local.

---

# 🏗 Arquitectura del proyecto

El proyecto sigue una arquitectura modular separada por responsabilidades:

```text
src/
├── config/        # Configuración global
├── llm/           # Cliente Ollama / lógica LLM
├── rag/           # Pipeline RAG / ingestion / retrieval
├── routing/       # Router de intenciones
├── tools/         # Herramientas externas integradas
└── utils/         # Utilidades auxiliares
```

---

# ⚙️ Stack tecnológico utilizado

### Backend / Core
- Python 3.13
- Ollama
- Streamlit

### IA / NLP
- SentenceTransformers
- Transformers
- LangChain

### Vector Database
- ChromaDB

### APIs externas
- Tavily Search API
- Open Meteo API

---

# 🧠 Flujo de procesamiento interno

El chatbot sigue el siguiente flujo lógico:

```text
Usuario →
Interfaz Streamlit →
Router de intenciones →
( Tool / RAG / LLM ) →
Respuesta final →
Usuario
```

---

# 📂 Sistema RAG

## Ingesta documental

Los documentos deben almacenarse en:

```text
data/raw/
```

Formatos recomendados:
- `.txt`
- `.md`

---

## Construcción de embeddings

Ejecutar:

```bash
python -m src.rag.ingestion
```

Esto:

1. Lee documentos.
2. Los fragmenta en chunks.
3. Genera embeddings.
4. Los almacena en ChromaDB.

---

# ▶️ Ejecución del proyecto

Lanzar la aplicación con:

```bash
streamlit run app.py
```

---

# 🔑 Variables de entorno necesarias

Crear archivo `.env`:

```env
TAVILY_API_KEY=TU_API_KEY
```

---

# 📌 Ejemplos de prompts soportados

### Chat general

```text
Explícame qué es machine learning
```

### Web Search

```text
Búscame noticias sobre inteligencia artificial en internet
```

### Weather

```text
Qué tiempo hará la próxima semana en Chipiona
```

### DateTime

```text
Qué hora es en Japón
```

### Calculator

```text
Calcula sqrt(144) + 8 * 2
```

### RAG

```text
Según mis documentos, ¿quién era Xylar?
```

---

# 🔮 Roadmap futuro

Próximas mejoras previstas:

- [ ] Streaming de respuesta en tiempo real.
- [ ] Memoria persistente.
- [ ] Upload de documentos desde UI.
- [ ] Citado de fuentes RAG.
- [ ] Multiagente / agent planning.
- [ ] Testing automatizado.
- [ ] Dockerización.

---

# 📖 Propósito del proyecto

Proyecto desarrollado como práctica personal para:

- profundizar en arquitectura de agentes IA,
- comprender integración real de tools + RAG,
- aprender buenas prácticas de software engineering en IA,
- crear una base escalable para versiones futuras.

---

# 👨‍💻 Autor

Desarrollado por Juan Antonio como proyecto personal de aprendizaje y portfolio.