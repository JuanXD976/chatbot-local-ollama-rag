# 🤖 Chatbot Local con Ollama — V2.0

Versión 2.0 final del proyecto, migrada a una arquitectura desacoplada con **FastAPI** como backend y **Next.js** como frontend, reutilizando el core modular de IA desarrollado en versiones anteriores.

Esta versión cierra la etapa de transición desde una app monolítica en Streamlit hacia una aplicación web real con separación entre interfaz, lógica de negocio, memoria, sesiones, tools y sistema RAG.

---

# 🚀 Qué incluye la V2.0

## Arquitectura desacoplada
- Backend con **FastAPI**
- Frontend con **Next.js + React + TypeScript**
- Comunicación entre frontend y backend mediante API HTTP

## Core IA reutilizado
- LLM local con **Ollama**
- Router de intenciones
- Tools externas
- RAG con **ChromaDB**
- Memoria persistente
- Gestión de sesiones

## Chat
- Chat conversacional desde web
- Streaming de respuestas
- Entrada de texto persistente
- Historial por sesión

## Sesiones
- Crear sesiones nuevas
- Cargar sesiones previas
- Eliminar sesiones
- Persistencia de conversaciones

## Memoria persistente
- Guardado de hechos explícitos del usuario
- Recuperación determinista para preguntas simples como:
  - nombre
  - trabajo
  - gustos
  - estudios
- Menor riesgo de respuestas inventadas en consultas de memoria

## RAG documental
- Gestión de documentos desde la interfaz web
- Soporte para:
  - `.txt`
  - `.md`
  - `.pdf`
  - `.docx`
- Subida e indexación automática de nuevos documentos
- Eliminación de documentos y embeddings asociados
- Reindexado global del corpus
- Estado visible de:
  - documentos cargados
  - chunks indexados
  - disponibilidad de base vectorial

## Limpieza de respuestas
- Eliminación de tokens internos del modelo
- Mejor control de residuos de plantillas tipo chat template
- Respuestas más limpias para UI web

---

# 🏗 Arquitectura general

```text
Usuario
   ↓
Next.js Frontend
   ↓
FastAPI Backend
   ↓
Core IA reutilizado
   ├── LLM local con Ollama
   ├── Router de intenciones
   ├── Tools
   ├── RAG con ChromaDB
   ├── Memoria persistente
   └── Sesiones
```
---
---

# 📂 Estructura del proyecto

```text
V1/
├── data/
│   ├── memory/
│   ├── raw/
│   └── vectorstore/
├── legacy/
│   └── streamlit_app.py
├── src/
│   ├── api/
│   ├── app/
│   ├── config/
│   ├── core/
│   ├── frontend/
│   ├── llm/
│   ├── memory/
│   ├── rag/
│   ├── routing/
│   ├── tools/
│   └── utils/
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```
---
---

# ⚙️ Backend (FastAPI)

La carpeta src/api/ contiene la capa API del proyecto.

- Endpoints principales
- GET /health
- POST /chat
- POST /chat/stream
- GET /sessions
- POST /sessions
- GET /sessions/{session_id}
- DELETE /sessions/{session_id}
- GET /documents
- POST /documents/upload
- DELETE /documents/{filename}
- POST /documents/rebuild
- POST /memory/reset

Swagger disponible en:
```text
http://localhost:8000/docs
```

# 🖥 Frontend (Next.js)

La carpeta src/frontend/ contiene el frontend del proyecto.

Funcionalidades actuales de interfaz:
- Sidebar de sesiones
- Gestión de memoria
- Gestión documental RAG
- Chat con streaming
- Estado de conexión del backend
- Render de respuestas enriquecidas con markdown

# 🧠 Core IA reutilizado

La lógica de inteligencia artificial sigue residiendo en src/:

- src/llm/ → cliente Ollama
- src/routing/ → router de intenciones
- src/rag/ → pipeline RAG, ingestion, retrieval y vectorstore
- src/memory/ → memoria persistente y extracción de hechos
- src/tools/ → tools externas
- src/app/ → servicios de aplicación, sesiones y documentos
---

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
- `.pdf`
- `.docx`

## Flujo documental actual
### Subir e indexar documento
- guarda el archivo
- lo indexa automáticamente
### Eliminar documento
- elimina el archivo físico
- elimina sus embeddings asociados
### Reindexar todo
- reindexa todos los documentos disponibles en data/raw
- pensado como acción de mantenimiento o reconstrucción global

---

## Construcción de embeddings

Ejecutar:

```bash
python -m src.rag.ingestion
```

Reconstrucción embeddings desde la UI:
- botón “Reconstruir Base Vectorial”

Esto:

1. Lee documentos.
2. Los fragmenta en chunks.
3. Genera embeddings.
4. Los almacena en ChromaDB.

---

# ▶️ Ejecución del proyecto

## 1. Backend

Desde la raíz del proyecto:
```bash
uvicorn src.api.main:app --reload
```
## 2. Frontend

Desde src/frontend:
```bash
npm install
npm run dev
```
## URLs
- Frontend: http://localhost:3000
- Backend: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
---

# 🔑 Variables de entorno necesarias

Crear archivo `.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=gemma3:4
OLLAMA_MAX_TOKENS=1200
LOG_LEVEL=INFO
TAVILY_API_KEY=TU_API_KEY
```
## Frontend (src/frontend/.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
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

### Memory

```text
Mi nombre es Juan
¿Cuál es mi nombre?
```
---

# 🔮 Roadmap futuro

Próximas mejoras previstas:

- [ ] rediseño visual más avanzado
- [ ] interfaz clara/blanca o temas seleccionables
- [ ] menú de administración tipo ⋯
- [ ] memoria y RAG fuera del sidebar principal
- [ ] configuración visual por usuario
- [ ] mejor gestión del markdown y del diseño del chat
- [ ] componentes React desacoplados
- [ ] mejoras de UX generales

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

---

# 7. Mi recomendación final de limpieza

Haz esto antes de seguir con nuevas mejoras:

## mover Streamlit a legacy
```text
legacy/streamlit/app_streamlit_v1.py
```
---