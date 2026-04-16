# 🤖 Chatbot Local con Ollama — V1.2.1

Versión 1.2.1 de un chatbot local desarrollado en Python utilizando **Streamlit**, **Ollama**, **RAG con ChromaDB**, **tools externas**, **memoria persistente** y **arquitectura modular profesional**.

El objetivo del proyecto es construir un asistente conversacional local escalable y modular que combine generación con LLM, herramientas externas, recuperación documental y memoria persistente, siguiendo buenas prácticas de software engineering aplicadas a IA.

---

# 🚀 Funcionalidades actuales

Actualmente el chatbot incorpora las siguientes capacidades:

---

## 💬 Chat conversacional local
- Generación de respuestas mediante modelo LLM local ejecutado en Ollama.
- Gestión de historial conversacional.
- Prompt de sistema configurable.
- Limitación de contexto mediante ventana de mensajes configurable.

---

## 🧠 Memoria persistente
- Sistema de memoria persistente entre sesiones.
- Capacidad para recordar información importante del usuario.
- Persistencia de datos aunque se cierre la aplicación.
- Botón para limpiar memoria desde la interfaz.
- Botón para iniciar nueva conversación sin perder memoria.
- Prevención de duplicados en memoria.

---

## 📂 Sistema de sesiones conversacionales
- Persistencia estructurada de conversaciones por sesión.
- Generación automática de `session_id`.
- Almacenamiento de histórico conversacional independiente.
- Gestión separada entre memoria persistente y sesiones de chat.

---

## 🌐 Búsqueda web en tiempo real
- Integración con Tavily Search API.
- Capacidad para buscar información actualizada en internet.
- Reformateo de resultados mediante LLM.

---

## 🌦 Consulta meteorológica avanzada
- Consulta meteorológica actual.
- Predicción diaria.
- Predicción semanal.
- Predicción próxima semana.
- Predicción próximo fin de semana.
- Resolución automática de ciudades mediante Open-Meteo Geocoding.

---

## 🕒 Fecha y hora inteligente
- Consulta de fecha/hora local.
- Consulta de hora por ubicación.
- Soporte para múltiples zonas horarias configuradas.

---

## 🧮 Calculadora integrada
- Resolución de operaciones matemáticas seguras.
- Soporte para:
  - suma
  - resta
  - multiplicación
  - división
  - potencias
  - módulo
  - sqrt
  - log
  - log10
  - trigonometría básica

---

## 📚 Sistema RAG local con ChromaDB
- Base vectorial local mediante Chroma.
- Embeddings con SentenceTransformers.
- Recuperación semántica de documentos propios.
- Pipeline RAG modular.
- Respuestas enriquecidas usando únicamente contexto recuperado.
- Formateo optimizado de contexto sin exposición de rutas técnicas.

---

## 📋 Logging y trazabilidad interna
- Sistema de logging centralizado.
- Registro de intención detectada.
- Registro de tools utilizadas.
- Registro de errores y excepciones.

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

- [ ] Historial visual de sesiones en sidebar.
- [ ] Recuperación de conversaciones anteriores.
- [ ]  Exportación de sesiones.
- [ ]  Upload de documentos desde UI.
- [ ]  Citado de fuentes RAG mejorado.
- [ ]  Streaming de respuesta en tiempo real.
- [ ]  Testing automatizado.
- [ ]  Backend desacoplado con FastAPI.
- [ ]  Frontend profesional con React/Next.js.
- [ ]  Dockerización.

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