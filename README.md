# 🤖 Chatbot Local con Ollama — V2.0

Versión 2.0 del proyecto, migrada a una arquitectura desacoplada con **FastAPI** como backend y **Next.js** como frontend, reutilizando el core modular de IA desarrollado en versiones anteriores.

El objetivo de esta versión es transformar el chatbot local en una aplicación más cercana a un entorno real de producto, separando claramente la capa de interfaz de usuario de la lógica de negocio, RAG, memoria, tools y sesiones.

---

# 🚀 Novedades principales de la V2.0

- Migración desde interfaz monolítica en Streamlit a arquitectura **frontend + backend**.
- Backend con **FastAPI**.
- Frontend con **Next.js + React + TypeScript**.
- Reutilización del core existente:
  - LLM local con Ollama
  - router de intenciones
  - tools
  - RAG
  - memoria persistente
  - sesiones
- Soporte para streaming de respuestas desde backend.
- Gestión documental del RAG desde interfaz web.
- Base preparada para seguir evolucionando hacia una arquitectura de producto más profesional.

---

# 🏗 Arquitectura

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
│   └── streamlit/
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
http://127.0.0.1:8000/docs
```

# 🖥 Frontend (Next.js)

La carpeta src/frontend/ contiene el frontend del proyecto.

- Funcionalidades actuales de interfaz
- Sidebar de sesiones
- Gestión de memoria persistente
- Gestión documental RAG
- Chat con streaming
- Consumo de backend vía API
- Base de diseño ya desacoplada del core Python

# 🧠 Core IA reutilizado

La lógica de inteligencia artificial sigue residiendo en src/:

- src/llm/ → cliente Ollama
- src/routing/ → router de intenciones
- src/rag/ → pipeline RAG
- src/memory/ → memoria persistente
- src/tools/ → tools externas
- src/app/ → servicios de aplicación, sesiones, documentos, orquestación
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
TAVILY_API_KEY=TU_API_KEY
OLLAMA_MAX_TOKENS=1200
OLLAMA_CHAT_MODEL=gemma3:4
LOG_LEVEL=INFO
```
## Frontend (src/frontend/.env.local)
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
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

- [ ] pulido visual del frontend
- [ ] limpieza completa de tokens residuales del modelo
- [ ] mejora del comportamiento del RAG
- [ ] componentes React separados
- [ ] mejora del sidebar y experiencia de usuario
- [ ] futura preparación para despliegue

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