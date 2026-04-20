# 🤖 Chatbot Local con Ollama — V5.0

Versión V5.0 del proyecto **Chatbot Local con Ollama**, centrada en mejorar la **inteligencia del sistema**, la **seguridad**, el **uso de RAG** y la **orquestación entre memoria, herramientas y documentos**.

Esta versión consolida una arquitectura local moderna con:

- **Frontend** en Next.js + React + TypeScript
- **Backend** en FastAPI
- **LLM local** con Ollama
- **RAG local** con ChromaDB
- **Memoria persistente**
- **Streaming**
- **Capa básica de seguridad** contra prompt injection

---

# 🚀 Novedades principales de la V5.0

## Inteligencia del sistema
- Detección de intención más robusta
- Uso automático de RAG cuando la consulta lo requiere
- Mejor separación entre:
  - memoria del usuario
  - contexto documental
  - tools
  - generación final del modelo

## Seguridad
- Bloqueo de peticiones de prompt injection
- Protección frente a intentos de revelar:
  - system prompt
  - instrucciones internas
  - contexto oculto
  - memoria completa
- Sanitización del contexto documental antes de pasarlo al modelo
- Limpieza de respuesta final para evitar tokens o restos internos

## RAG mejorado
- Respuestas documentales más limpias
- Fuentes consultadas al final de la respuesta
- Heurísticas para no forzar RAG cuando no hay contexto útil

## Memoria
- Uso más controlado de la memoria persistente
- Respuestas personales más directas
- Menor mezcla de datos personales en respuestas no relacionadas

---

# 🧱 Arquitectura general

```text
Usuario
   ↓
Next.js Frontend
   ↓
FastAPI Backend
   ↓
Core IA local
   ├── Router de intenciones
   ├── Prompt Guard (seguridad)
   ├── Memoria persistente
   ├── RAG / recuperación documental
   ├── Tools
   └── LLM local con Ollama
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
│   │   │   ├── components/
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── lib/
│   │   ├── next-env.d.ts
│   │   ├── next.config.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── llm/
│   ├── memory/
│   ├── rag/
│   ├── routing/
│   ├── security/
│   │    ├── prompt_guard.py
│   │    ├── context_sanitizer.py
│   │    └── response_guard.py
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
- Sidebar de sesiones
- Chat con streaming
- Panel de administración con pestañas
- Tema claro / oscuro / auto
- Renderizado markdown
- Gestión documental RAG
- Drag & drop para documentos
- Subida múltiple de archivos
- Menús ⋯ para acciones secundarias

## Componentes principales
- SessionList.tsx
- MessageBubble.tsx
- ChatComposer.tsx
- AdminPanel.tsx
- UploadDropzone.tsx

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
- admite drag & drop
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
# ✅ Estado actual de la V5.0
La V5.0 deja resueltos estos bloques:

- arquitectura local moderna
- frontend modular
- sesiones persistentes
- memoria persistente funcional
- streaming operativo
- RAG local con fuentes
- subida múltiple de documentos
- drag & drop documental
- panel de administración
- tema visual
- capa de seguridad contra prompt injection
- sanitización de contexto documental
- limpieza de respuestas internas del modelo

# 🔮 Roadmap futuro

El siguiente paso natural del proyecto sería una versión posterior centrada en capacidades más avanzadas, por ejemplo:

- [ ] subir imágenes al chat
- [ ] analizar imágenes y archivos directamente en la conversación
- [ ] vista previa de adjuntos
- [ ] contexto temporal por archivo
- [ ] integración del análisis visual con el flujo conversacional

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