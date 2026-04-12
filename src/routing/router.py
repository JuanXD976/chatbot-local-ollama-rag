"""
Router de intenciones del chatbot.

Motivo de su creación:
- Decidir si una consulta debe resolverse con el LLM, con una tool o con RAG.
- Mantener separada la lógica de enrutado del resto de la aplicación.
"""

from __future__ import annotations

import re

from src.llm.ollama_client import generate_response, format_tool_result_with_llm
from src.rag.pipeline import answer_with_rag
from src.tools.tools import (
    calculate_expression,
    get_current_datetime,
    get_weather,
    search_web,
)


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

def process_user_message(prompt: str, messages: list[dict[str, str]]) -> str:
    """
    Procesa el mensaje del usuario decidiendo si usar tools, RAG o el modelo.
    """
    intent = detect_intent(prompt)
    
    print(f"[ROUTER] Intent detectada: {intent}")
    
    if intent == "datetime":
        location = extract_datetime_location(prompt)
        raw_result = get_current_datetime(location)
        
        print(f"[DATETIME] Ubicación detectada: {location}")
        
        return format_tool_result_with_llm(
            user_prompt=prompt,
            tool_name="datetime",
            tool_result=raw_result,
        )

    if intent == "weather":
        city = extract_city(prompt)
        scope = detect_weather_scope(prompt)
        raw_result = get_weather(city, scope=scope)
        
        print(f"[WEATHER] Ciudad: {city} | Scope: {scope}")
        
        # Para salidas estructuradas, mejor no usar el LLM
        if scope in ["weekly", "next_week", "next_weekend"]:
            return raw_result

        return format_tool_result_with_llm(
            user_prompt=prompt,
            tool_name="weather",
            tool_result=raw_result,
        )

    if intent == "web":
        print("[WEB] Ejecutando búsqueda web")
        
        raw_result = search_web(prompt)
        return format_tool_result_with_llm(
            user_prompt=prompt,
            tool_name="web_search",
            tool_result=raw_result,
        )
        
    if intent == "rag":
        print("[RAG] Ejecutando pipeline RAG")
        return answer_with_rag(prompt)
    
    if intent == "calculator":
        expression = extract_expression(prompt)
        print(f"[CALCULATOR] Expresión: {expression}")
        return calculate_expression(expression)
    
    print("[CHAT] Respuesta directa con LLM")
    return generate_response(messages)