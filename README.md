# 🤖 Chatbot Local con Ollama — V8 Final

Versión **V8 Final** del proyecto **Chatbot Local con Ollama**, una aplicación local de inteligencia artificial con arquitectura modular, soporte multimodal, RAG persistente y experiencia de uso tipo chat profesional.

Esta versión integra:

- 🧠 IA local con **Ollama**
- 📎 Soporte de adjuntos (**PDF, CSV, DOCX, XLSX, TXT, imágenes**)
- 🌍 Respuesta automática en el **idioma del usuario**
- 📚 **RAG persistente** con recuperación híbrida y reranking
- ⚡ Streaming en tiempo real + botón **STOP**
- 💾 Sesiones persistentes
- 🧩 Arquitectura modular escalable
- 🎯 UX avanzada tipo ChatGPT

---

# 🚀 Características principales

## 🧠 Inteligencia del sistema
- Detección automática de intención
- Selección automática de modo de respuesta
- Generación estructurada:
  - código
  - tablas
  - análisis
  - resúmenes
- Control automático del formato de salida
- Respuesta híbrida:
  - usa RAG si aporta valor
  - responde con conocimiento general si el contexto documental no cubre la pregunta

## 🌍 Multiidioma automático
- Detecta automáticamente el idioma principal del usuario
- Responde en ese mismo idioma
- Evita que el idioma del documento fuerce el idioma de salida

## 📎 Soporte de archivos
- PDF → extracción de texto
- DOCX → extracción de texto
- CSV → análisis estructurado
- XLSX → extracción y resumen tabular
- Imágenes → análisis visual con modelo de visión + fallback
- Uso del contenido como contexto real en la respuesta

## 📚 Sistema RAG
- Embeddings persistentes
- Almacenamiento vectorial local
- Recuperación híbrida:
  - vectorial
  - keyword
- Reranking de resultados
- Contexto documental inteligente

## ⚡ Streaming
- Respuesta en tiempo real
- Mejora de UX
- Posibilidad de interrumpir la generación (STOP)

## 💬 Sesiones
- Historial persistente
- Cambio entre conversaciones
- Contexto mantenido por sesión

## 💻 UX avanzada
- Render profesional de código
- Tablas limpias y legibles
- Botón copiar contextual
- Input con auto-resize
- Sidebar de sesiones
- Panel de administración
- Tema claro / oscuro / auto

---

# 🧱 Arquitectura

```text
Usuario
   ↓
Frontend (Next.js)
   ↓
Backend (FastAPI)
   ↓
Core IA
   ├── Gestión de sesiones
   ├── Procesado de archivos
   ├── Inyección de contexto
   ├── Routing / modos automáticos
   ├── Control de formato
   ├── RAG persistente
   └── LLM local (Ollama)
```

---

# 📂 Estructura del proyecto

```text
chatbot-ia/
├── data/
│   ├── memory/
│   ├── raw/
│   └── vectorstore/
├── src/
│   ├── agents/
│   ├── api/
│   ├── app/
│   ├── attachments/
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
│   ├── tools/
│   └── utils/
├── .env
├── .gitignore
├── README.md
├── launch_chatbot.bat
├── stop_chatbot.bat
└── requirements.txt

```

---

# ⚙️ Requisitos previos

Antes de ejecutar el proyecto necesitas tener instalado:

## 1. Python
- **Python 3.11 o superior** recomendado

## 2. Node.js
- **Node.js 18 o superior** recomendado

## 3. Ollama
Descárgalo e instálalo desde:

- https://ollama.com/download

## 4. Modelos Ollama necesarios

### Modelo principal de chat
```bash
ollama pull gemma3:4b
```

### Modelo visual
Debes tener al menos uno de estos:

```bash
ollama pull qwen2.5vl:7b
```

Si tu equipo no puede mover ese modelo por RAM, puedes usar el fallback ya configurado:

```bash
ollama pull gemma3:4b
ollama pull gemma3:4
```

> Nota: `qwen2.5vl:7b` puede requerir bastante memoria. Si falla, el sistema intentará usar fallback.

## 5. Dependencias Python
Desde la raíz del proyecto:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 6. Dependencias Frontend
Desde `src/frontend`:

```bash
npm install
```

## 7. Configuración

## Archivo `.env` en raíz

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=gemma3:4b
OLLAMA_VISION_MODEL=qwen2.5vl:7b
OLLAMA_MAX_TOKENS=1200
LOG_LEVEL=INFO
TAVILY_API_KEY=TU_API_KEY
```

## Archivo `src/frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

# 📂 Sistema documental RAG

## Carpeta documental
Los documentos se almacenan en:

```text
data/raw/
```

## Flujo documental actual
- Subida múltiple de documentos
- Drag & drop
- Indexación automática al subir
- Eliminación del archivo físico
- Eliminación de embeddings asociados
- Reindexación completa desde UI

## Formatos recomendados para RAG
- `.txt`
- `.md`
- `.pdf`
- `.docx`
- `.csv`
- `.xlsx`

---

# ⚙️ Backend (FastAPI)

La carpeta `src/api/` contiene la capa API.

## Endpoints principales
- `GET /health`
- `POST /chat`
- `POST /chat/stream`
- `POST /chat/attachments`
- `POST /exports/response`
- `GET /sessions`
- `POST /sessions`
- `GET /sessions/{session_id}`
- `DELETE /sessions/{session_id}`
- `GET /documents`
- `POST /documents/upload`
- `DELETE /documents/{filename}`
- `POST /documents/rebuild`
- `POST /memory/reset`

## Swagger
Disponible en:

```text
http://localhost:8000/docs
```

---

# 🖥 Frontend (Next.js)

La carpeta `src/frontend/` contiene el frontend del proyecto.

## Funcionalidades actuales de interfaz
- Sidebar de sesiones
- Chat con streaming
- Soporte de adjuntos
- Panel de administración
- Tema claro / oscuro / auto
- Renderizado markdown
- Renderizado avanzado de código
- Renderizado avanzado de tablas
- Gestión documental RAG
- Drag & drop para documentos
- Subida múltiple de archivos
- Menús `⋯` para acciones secundarias
- Botón STOP durante generación

## Componentes principales
- `SessionList.tsx`
- `MessageBubble.tsx`
- `AttachmentComposer.tsx`
- `AdminPanel.tsx`
- `UploadDropzone.tsx`

---

# ▶️ Ejecución manual

## 1. Levantar Ollama
En una terminal:

```bash
ollama serve
```

## 2. Levantar backend
En otra terminal, desde la raíz:

```bash
venv\Scripts\activate
uvicorn src.api.main:app --reload
```

## 3. Levantar frontend
En otra terminal, desde `src/frontend`:

```bash
npm run dev
```

## URLs
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs

---

# 🧪 Ejemplos de uso

## Chat general
```text
Explícame qué es machine learning
```

## Código
```text
Dame un script en Python para hacer una cuenta atrás de 1000 a 0 de 2 en 2
```

## Tabla
```text
Hazme una tabla markdown con 3 columnas sobre bases de datos vectoriales
```

## PDF
```text
Resúmeme este PDF en 5 puntos
```

## CSV
```text
Analiza este CSV en español y dame una tabla con 3 columnas
```

## Imagen
```text
Kannst du den Fehler oder die wichtigen Informationen auf diesem Screenshot analysieren?
```

## Multiidioma
```text
Can you explain this document in English?
Peux-tu me faire un résumé clair de ce document ?
```

---

# 🚀 Lanzador automático

Este proyecto incluye scripts para ejecutar y detener todo el sistema de forma automática, sin necesidad de abrir múltiples terminales manualmente.

---
## ▶️ Iniciar el chatbot

Archivo:

```text
launch_chatbot.bat
```

## ▶️ Parar el chatbot

Archivo:

```text
stop_chatbot.bat
```
---

# ⚠️ Limitaciones actuales

- El modelo visual puede requerir bastante RAM
- La calidad del análisis depende del modelo local instalado
- El RAG está muy bien resuelto para uso local, pero no es una arquitectura distribuida
- Los workflows automáticos son ligeros, no una orquestación multiagente compleja

---

# 🔮 Posicionamiento de esta versión

Esta versión puede considerarse ya como una versión final sólida para:

- portfolio
- uso personal
- base de proyectos más avanzados
- demostración técnica en GitHub y LinkedIn

---

# 📖 Propósito del proyecto

Proyecto desarrollado para:

- aprender arquitectura real de sistemas IA
- integrar LLMs locales en una aplicación completa
- construir una base sólida reutilizable para otros proyectos
- practicar RAG, adjuntos, multimodalidad y UX aplicada a IA

---

# 👨‍💻 Autor

Desarrollado por **Juan Antonio** como proyecto personal de aprendizaje, portfolio y base técnica para futuros proyectos de IA.
