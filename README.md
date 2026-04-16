# 🤖 Chatbot Local con Ollama — V1.3

Versión 1.3 de un chatbot local desarrollado en Python utilizando **Streamlit**, **Ollama**, **RAG con ChromaDB**, **tools externas**, **memoria persistente**, **sesiones conversacionales** y **arquitectura modular profesional**.

El objetivo del proyecto es construir un asistente conversacional local escalable y modular que combine generación con LLM, herramientas externas, recuperación documental y memoria persistente, siguiendo buenas prácticas de software engineering aplicadas a IA.

---

# 🚀 Funcionalidades actuales

## 💬 Chat conversacional local
- Generación de respuestas mediante modelo LLM local ejecutado en Ollama.
- Gestión de historial conversacional.
- Prompt de sistema configurable.
- Limitación de contexto mediante ventana configurable.

---

## 🧠 Memoria persistente
- Persistencia entre sesiones.
- Recordatorio de información importante del usuario.
- Prevención de duplicados.
- Limpieza manual desde interfaz.

---

## 📂 Gestión visual de sesiones
- Sidebar de historial conversacional.
- Creación de nuevas conversaciones.
- Carga de sesiones anteriores.
- Eliminación de sesiones.
- Exportación de sesiones en JSON.
- Resaltado visual de sesión activa.

---

## 🌐 Búsqueda web
- Integración con Tavily Search API.
- Información en tiempo real desde internet.
- Reformateo natural mediante LLM.

---

## 🌦 Weather Tool
- Tiempo actual.
- Predicción semanal.
- Predicción próxima semana.
- Predicción fin de semana.
- Geocoding automático de ciudades.

---

## 🕒 DateTime Tool
- Hora actual.
- Fecha actual.
- Hora por ubicación.

---

## 🧮 Calculadora
- Operaciones matemáticas seguras.
- Soporte para:
  - suma/resta
  - multiplicación/división
  - sqrt/log/log10
  - trigonometría

---

## 📚 Sistema RAG
- Base vectorial local con ChromaDB.
- Recuperación semántica de documentos.
- Embeddings con SentenceTransformers.
- Prompt RAG optimizado.
- Limpieza de metadatos/rutas técnicas.

---

## 📋 Logging interno
- Registro de flujo de ejecución.
- Registro de intención detectada.
- Registro de tools usadas.
- Registro de errores.

---

# 🏗 Arquitectura del proyecto

El proyecto sigue una arquitectura modular profesional separada por responsabilidades:

```text
src/
├── app/            # Capa de aplicación / servicios / orquestación
├── config/         # Configuración global / logging / settings
├── core/           # Modelos internos / excepciones custom
├── llm/            # Cliente Ollama / generación LLM
├── memory/         # Memoria persistente / storage
├── rag/            # Pipeline RAG / ingestion / retrieval / vectorstore
├── routing/        # Router de intenciones
├── tools/          # Herramientas externas integradas
└── utils/          # Utilidades auxiliares
```
---

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
- Open Meteo Geocoding API

---

---

# 🧠 Flujo de procesamiento interno

El chatbot sigue el siguiente flujo lógico:

```text
Usuario
   ↓
Interfaz Streamlit
   ↓
ChatService
   ↓
ChatOrchestrator
   ↓
Router de intenciones
   ↓
( Tool / RAG / LLM )
   ↓
Respuesta estructurada
   ↓
Usuario
```
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

### Memory

```text
Mi nombre es Juan
¿Cuál es mi nombre?
```
---

# 🔮 Roadmap futuro

Próximas mejoras previstas:

- [ ] Streaming de respuesta en tiempo real.
- [ ] Upload de documentos desde UI.
- [ ] Smart Memory Manager.
- [ ] Backend desacoplado FastAPI.
- [ ] Frontend React/Next.js.
- [ ] Dockerización.
- [ ] Testing automatizado.

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