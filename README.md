# 🤖 Chatbot Local con Ollama — V1.6

Versión 1.6 de un chatbot local desarrollado en Python utilizando **Streamlit**, **Ollama**, **RAG con ChromaDB**, **tools externas**, **memoria persistente**, **sesiones conversacionales**, **streaming en tiempo real** y **gestión documental completa**.

El objetivo del proyecto es construir un asistente conversacional local escalable y modular que combine generación con LLM, herramientas externas, recuperación documental y memoria persistente, siguiendo buenas prácticas de software engineering aplicadas a IA.

---

# 🚀 Funcionalidades actuales

## 💬 Chat conversacional local
- Generación de respuestas mediante modelo LLM local ejecutado en Ollama.
- Gestión de historial conversacional.
- Prompt de sistema configurable.
- Limitación de contexto mediante ventana configurable.

---

## ⚡ Streaming de respuesta en tiempo real
- Respuesta progresiva chunk a chunk.
- Renderizado dinámico tipo ChatGPT.
- Indicador visual de "pensando".
- Limpieza automática de tokens internos y residuos del modelo.
- Soporte para respuestas largas mejorado.
- Streaming también para respuestas documentales RAG.

---

## 🧠 Memoria persistente mejorada
- Persistencia entre sesiones.
- Recordatorio de información importante del usuario.
- Prevención de duplicados.
- Extracción más inteligente de hechos útiles del usuario.
- Evita guardar ruido innecesario como prompts temporales.
- Limpieza manual desde la interfaz.

---

## 📂 Gestión visual de sesiones
- Sidebar de historial conversacional.
- Creación de nuevas conversaciones.
- Carga de sesiones anteriores.
- Eliminación de sesiones.
- Exportación de sesiones en JSON.
- Resaltado visual de sesión activa.

---

## 📚 Gestión documental completa para RAG
- Subida de documentos desde la interfaz.
- Listado de documentos cargados.
- Eliminación individual de documentos.
- Reconstrucción de la base vectorial desde UI.
- Estado visual del módulo documental.
- Prevención de sobreescritura accidental de archivos.
- Manejo robusto de errores de reconstrucción.

---

## 📄 Soporte de formatos documentales
Formatos soportados actualmente:
- `.txt`
- `.md`
- `.pdf`
- `.docx`

---

## 🌐 Búsqueda web
- Integración con Tavily Search API.
- Información en tiempo real desde internet.
- Reformateo natural mediante LLM.

---

## 🌦 Weather Tool
- Tiempo actual.
- Predicción diaria.
- Predicción semanal.
- Predicción próxima semana.
- Predicción próximo fin de semana.
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
  - potencias
  - módulo
  - sqrt/log/log10
  - trigonometría básica

---

## 📋 Logging interno
- Registro de flujo de ejecución.
- Registro de intención detectada.
- Registro de tools usadas.
- Registro de errores.

---

# 🏗 Arquitectura

```text
src/
├── app/            # Servicios de aplicación / orquestación / documentos / sesiones
├── config/         # Configuración global / logging / settings
├── core/           # Modelos internos / excepciones personalizadas
├── llm/            # Cliente Ollama / generación / streaming
├── memory/         # Memoria persistente / extracción de memoria útil
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

### Document processing
- PyPDF
- Docx2txt

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

Lanzar la aplicación con:

```bash
streamlit run app.py
```

---

# 🔑 Variables de entorno necesarias

Crear archivo `.env`:

```env
TAVILY_API_KEY=TU_API_KEY
OLLAMA_MAX_TOKENS=1200
OLLAMA_CHAT_MODEL=gemma3:4
LOG_LEVEL=INFO
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

- [ ] Migración a backend FastAPI.
- [ ] Migración a frontend React / Next.js.
- [ ] Separación completa entre frontend y backend.
- [ ] Consumo de endpoints vía API.
- [ ] Arquitectura más cercana a entorno de producción.

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