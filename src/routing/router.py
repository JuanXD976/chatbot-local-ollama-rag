"""
Router de intenciones del chatbot.

Motivo de su creación:
- Decidir si una consulta debe resolverse con el LLM, con una tool o con RAG.
- Mantener separada la lógica de enrutado del resto de la aplicación.
"""

from __future__ import annotations

import logging
import re

from src.llm.ollama_client import generate_response, format_tool_result_with_llm
from src.rag.pipeline import answer_with_rag
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
        "en mis documentos",
        "en la base local",
        "en la base de conocimiento",
        "en mis apuntes",
        "según la documentación",
        "busca en local",
        "busca en mis archivos",
        "archivos propios",
        "busca en nuestra base de datos",
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


def extract_city(prompt: str) -> str:
    """
    Extracción simple de ciudad desde el prompt.
    """
    match = re.search(r"\ben\s+([a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+)", prompt, re.IGNORECASE)
    if match:
        return match.group(1).strip(" ?¿!.,")
    return "Madrid"

def extract_expression(prompt: str) -> str:
    """
    Intenta extraer una expresión matemática simple del prompt.
    """
    expression = prompt.lower()
    expression = expression.replace("cuánto es", "")
    expression = expression.replace("cuanto es", "")
    expression = expression.replace("calcula", "")
    expression = expression.strip()

    # Correcciones simples
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
    """
    Extrae una ubicación simple para consultas de fecha y hora.
    """
    match = re.search(r"\ben\s+([a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+)", prompt, re.IGNORECASE)
    if match:
        return match.group(1).strip(" ?¿!.,")
    return None

def execute_user_message(prompt: str, messages: list[dict[str, str]]) -> dict:
    """
    Procesa el mensaje del usuario y devuelve una respuesta estructurada.
    """
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


def process_user_message(prompt: str, messages: list[dict[str, str]]) -> str:
    """
    Mantiene compatibilidad con la V1.1 devolviendo solo texto.
    """
    result = execute_user_message(prompt, messages)
    return result["answer"]