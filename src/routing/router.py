"""
Router de intenciones del chatbot.

Motivo de su creación:
- Decidir si una consulta debe resolverse con el LLM, con una tool o con RAG.
- Mantener separada la lógica de enrutado del resto de la aplicación.
"""

from __future__ import annotations

import logging
import re

from src.llm.ollama_client import (
    format_tool_result_with_llm,
    format_tool_result_with_llm_stream,
    generate_response,
    generate_response_stream,
)
from src.memory.memory_service import answer_memory_question
from src.rag.pipeline import answer_with_rag, answer_with_rag_stream
from src.tools.tools import (
    calculate_expression,
    get_current_datetime,
    get_weather,
    search_web,
)

logger = logging.getLogger(__name__)


def detect_intent(prompt: str) -> str:
    """
    Detecta la intención principal del mensaje del usuario.
    """
    prompt_lower = prompt.lower()

    weather_keywords = ["tiempo", "clima", "temperatura", "lluvia", "sol", "viento"]
    datetime_keywords = ["hora", "fecha", "qué día es", "que dia es", "qué hora es", "que hora es"]
    web_keywords = [
        "busca en internet",
        "búscame",
        "buscame",
        "últimas noticias",
        "ultimas noticias",
        "qué ha pasado",
        "que ha pasado",
        "buscar en internet",
        "en internet",
    ]

    rag_keywords = [
        "según mis documentos",
        "segun mis documentos",
        "en mis documentos",
        "mis documentos",
        "mis archivos",
        "mis pdf",
        "mis pdfs",
        "mis docx",
        "mi documentación",
        "mi documentacion",
        "mi base de datos",
        "mi base documental",
        "mi base local",
        "mi base de conocimiento",
        "busca en mis documentos",
        "busca en mis archivos",
        "revisa mis documentos",
        "revisa mis archivos",
        "consulta mis documentos",
        "consulta mis archivos",
        "en la base local",
        "en la base de conocimiento",
        "archivos propios",
        "nuestra bbdd",
    ]

    calc_keywords = ["calcula", "cuánto es", "cuanto es", "+", "-", "*", "/", "sqrt", "log"]

    if any(keyword in prompt_lower for keyword in weather_keywords):
        return "weather"

    if any(keyword in prompt_lower for keyword in datetime_keywords):
        return "datetime"

    if any(keyword in prompt_lower for keyword in web_keywords):
        return "web"

    if any(keyword in prompt_lower for keyword in rag_keywords):
        return "rag"

    if any(keyword in prompt_lower for keyword in calc_keywords):
        return "calculator"

    return "chat"


def is_memory_question(prompt: str) -> bool:
    prompt_lower = prompt.lower()

    memory_questions = [
        "cómo me llamo",
        "como me llamo",
        "cuál es mi nombre",
        "cual es mi nombre",
        "dónde trabajo",
        "donde trabajo",
        "en qué trabajo",
        "en que trabajo",
        "qué me gusta",
        "que me gusta",
        "dónde vivo",
        "donde vivo",
        "qué estudio",
        "que estudio",
    ]

    return any(q in prompt_lower for q in memory_questions)


def extract_city(prompt: str) -> str:
    match = re.search(r"\ben\s+([a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+)", prompt, re.IGNORECASE)
    if match:
        return match.group(1).strip(" ?¿!.,")
    return "Madrid"


def extract_expression(prompt: str) -> str:
    expression = prompt.lower()
    expression = expression.replace("cuánto es", "")
    expression = expression.replace("cuanto es", "")
    expression = expression.replace("calcula", "")
    expression = expression.strip()
    expression = expression.replace("sqtr", "sqrt")
    return expression


def detect_weather_scope(prompt: str) -> str:
    prompt_lower = prompt.lower()

    weather_scope_map = {
        "next_week": [
            "próxima semana",
            "proxima semana",
            "siguiente semana",
        ],
        "next_weekend": [
            "próximo fin de semana",
            "proximo fin de semana",
            "siguiente fin de semana",
        ],
        "weekly": [
            "esta semana",
            "toda la semana",
        ],
        "tomorrow": [
            "mañana",
        ],
        "today": [
            "hoy",
        ],
    }

    for scope, keywords in weather_scope_map.items():
        if any(keyword in prompt_lower for keyword in keywords):
            return scope

    return "current"


def extract_datetime_location(prompt: str) -> str | None:
    match = re.search(
        r"\ben\s+([a-zA-ZáéíóúÁÉÍÓÚñÑ\s,\-]+)",
        prompt,
        re.IGNORECASE,
    )

    if not match:
        return None

    location = match.group(1).strip(" ?¿!.,")
    location = location.replace(",", " ")
    location = re.sub(r"\s+", " ", location)

    return location.strip()


def execute_user_message(prompt: str, messages: list[dict[str, str]]) -> dict:
    """
    Procesa el mensaje del usuario y devuelve una respuesta estructurada.
    """
    memory_answer = answer_memory_question(prompt)
    if memory_answer is not None:
        return {
            "answer": memory_answer,
            "detected_intent": "memory",
            "tools_used": ["memory"],
            "sources": ["persistent_memory"],
        }

    intent = detect_intent(prompt)

    logger.info("Intent detectada: %s", intent)

    if intent == "datetime":
        location = extract_datetime_location(prompt)
        raw_result = get_current_datetime(location)

        logger.info("Datetime location=%s", location)

        return {
            "answer": format_tool_result_with_llm(
                user_prompt=prompt,
                tool_name="datetime",
                tool_result=raw_result,
            ),
            "detected_intent": "datetime",
            "tools_used": ["datetime"],
            "sources": [],
        }

    if intent == "weather":
        city = extract_city(prompt)
        scope = detect_weather_scope(prompt)
        raw_result = get_weather(city, scope=scope)

        logger.info("Weather city=%s scope=%s", city, scope)

        if scope in ["weekly", "next_week", "next_weekend"]:
            return {
                "answer": raw_result,
                "detected_intent": "weather",
                "tools_used": ["weather"],
                "sources": [],
            }

        return {
            "answer": format_tool_result_with_llm(
                user_prompt=prompt,
                tool_name="weather",
                tool_result=raw_result,
            ),
            "detected_intent": "weather",
            "tools_used": ["weather"],
            "sources": [],
        }

    if intent == "web":
        logger.info("Ejecutando búsqueda web")
        raw_result = search_web(prompt)

        return {
            "answer": format_tool_result_with_llm(
                user_prompt=prompt,
                tool_name="web_search",
                tool_result=raw_result,
            ),
            "detected_intent": "web",
            "tools_used": ["web_search"],
            "sources": [],
        }

    if intent == "rag":
        logger.info("Ejecutando pipeline RAG")
        return {
            "answer": answer_with_rag(prompt),
            "detected_intent": "rag",
            "tools_used": ["rag"],
            "sources": ["local_knowledge_base"],
        }

    if intent == "calculator":
        expression = extract_expression(prompt)
        logger.info("Calculator expression=%s", expression)

        return {
            "answer": calculate_expression(expression),
            "detected_intent": "calculator",
            "tools_used": ["calculator"],
            "sources": [],
        }

    logger.info("Respuesta directa con LLM")
    return {
        "answer": generate_response(messages),
        "detected_intent": "chat",
        "tools_used": [],
        "sources": [],
    }


def stream_user_message(prompt: str, messages: list[dict[str, str]]) -> dict:
    """
    Variante streaming. Devuelve un generador en los casos soportados.
    Para tool outputs estructurados o respuestas no streamables, devuelve texto completo.
    """
    memory_answer = answer_memory_question(prompt)
    if memory_answer is not None:
        return {
            "answer": memory_answer,
            "detected_intent": "memory",
            "tools_used": ["memory"],
            "sources": ["persistent_memory"],
        }

    intent = detect_intent(prompt)

    logger.info("Intent detectada (stream): %s", intent)

    if intent == "datetime":
        location = extract_datetime_location(prompt)
        raw_result = get_current_datetime(location)

        return {
            "stream": format_tool_result_with_llm_stream(
                user_prompt=prompt,
                tool_name="datetime",
                tool_result=raw_result,
            ),
            "detected_intent": "datetime",
            "tools_used": ["datetime"],
            "sources": [],
        }

    if intent == "weather":
        city = extract_city(prompt)
        scope = detect_weather_scope(prompt)
        raw_result = get_weather(city, scope=scope)

        if scope in ["weekly", "next_week", "next_weekend"]:
            return {
                "answer": raw_result,
                "detected_intent": "weather",
                "tools_used": ["weather"],
                "sources": [],
            }

        return {
            "stream": format_tool_result_with_llm_stream(
                user_prompt=prompt,
                tool_name="weather",
                tool_result=raw_result,
            ),
            "detected_intent": "weather",
            "tools_used": ["weather"],
            "sources": [],
        }

    if intent == "web":
        raw_result = search_web(prompt)
        return {
            "stream": format_tool_result_with_llm_stream(
                user_prompt=prompt,
                tool_name="web_search",
                tool_result=raw_result,
            ),
            "detected_intent": "web",
            "tools_used": ["web_search"],
            "sources": [],
        }

    if intent == "rag":
        return {
            "stream": answer_with_rag_stream(prompt),
            "detected_intent": "rag",
            "tools_used": ["rag"],
            "sources": ["local_knowledge_base"],
        }

    if intent == "calculator":
        expression = extract_expression(prompt)
        return {
            "answer": calculate_expression(expression),
            "detected_intent": "calculator",
            "tools_used": ["calculator"],
            "sources": [],
        }

    return {
        "stream": generate_response_stream(messages),
        "detected_intent": "chat",
        "tools_used": [],
        "sources": [],
    }


def process_user_message(prompt: str, messages: list[dict[str, str]]) -> str:
    result = execute_user_message(prompt, messages)
    return result["answer"]