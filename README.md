# 🤖 Chatbot Local con Ollama — V3.0

Versión V3.0 del proyecto **Chatbot Local con Ollama**, evolucionado hacia una aplicación web con arquitectura desacoplada, experiencia de usuario mejorada y panel de administración integrado.

Esta versión consolida la migración desde una app experimental en Streamlit hacia una solución más seria basada en **FastAPI + Next.js**, manteniendo el core modular de IA, RAG, memoria persistente, sesiones y tools.

---

# 🚀 Qué incluye la V3.0

## Frontend mejorado
- Interfaz web con **Next.js + React + TypeScript**
- Tema visual claro / oscuro / automático
- Mensajes del usuario alineados a la derecha
- Mensajes del asistente alineados a la izquierda
- Markdown renderizado en respuestas del asistente
- Menús contextuales `⋯` para sesiones y documentos
- Panel lateral de administración con:
  - memoria persistente
  - base documental RAG
  - estado del sistema
  - selector de tema

## Backend consolidado
- API REST con **FastAPI**
- Endpoint de streaming para respuestas progresivas
- Gestión de sesiones conversacionales
- Memoria persistente del usuario
- Integración con Ollama
- Sistema RAG con indexación documental automática

## Gestión documental RAG
- Subida de múltiples archivos a la vez
- Indexación automática al subir documentos
- Eliminación de documentos y embeddings asociados
- Reindexado global del corpus como tarea de mantenimiento
- Soporte para:
  - `.txt`
  - `.md`
  - `.pdf`
  - `.docx`

## Memoria persistente
- Guarda hechos explícitos del usuario
- Respuesta determinista para preguntas simples:
  - nombre
  - trabajo
  - gustos
  - lugar de residencia
  - estudios

## Limpieza de respuestas
- Eliminación de residuos de plantillas del modelo
- Reducción de tokens extraños en salida
- Mejor control del streaming y de los stop tokens

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
   ├── Memoria persistente
   ├── Sesiones
   └── RAG con ChromaDB
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
├── docs/
├── legacy_streamlit/
│   └── app_streamlit_v1.py
├── src/
│   ├── api/
│   ├── app/
│   ├── config/
│   ├── core/
│   ├── frontend/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
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

## Endpoints principales
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
- Sidebar centrado en sesiones
- Panel ⋯ de administración
- Tema claro / oscuro / auto
- Chat con streaming
- Renderizado markdown
- Gestión documental integrada
- Menús contextuales para eliminar sesiones y documentos

# 🧠 Core IA

La lógica de inteligencia artificial sigue residiendo en src/:

- src/llm/ → cliente Ollama
- src/routing/ → router de intenciones
- src/rag/ → ingestion, retrieval, vectorstore y pipeline RAG
- src/memory/ → memoria persistente y extracción de hechos
- src/tools/ → weather, datetime, cálculo, búsqueda web
- src/app/ → servicios de chat, sesiones y documentos
- src/api/ → endpoints FastAPI
- src/frontend/ → interfaz Next.js
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
### Subida documental
- permite subir varios archivos a la vez
- guarda cada archivo
- indexa automáticamente cada documento
### Eliminar documento
- elimina el archivo físico
- elimina sus embeddings asociados
### Reindexar todo
- reprocesa todos los documentos presentes en data/raw
- pensado como operación de mantenimiento
---
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
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs
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

- [ ] persistencia de preferencias de usuario
- [ ] componentes React más desacoplados
- [ ] drag & drop para documentos
- [ ] mejor RAG con citas y fuentes visibles
- [ ] mejoras de UX móvil
- [ ] ajustes más avanzados de memoria y administración

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