"""
Herramientas auxiliares del chatbot.

Motivo de su creación:
- Centralizar funciones externas al modelo.
- Permitir acceso a información dinámica y cálculos fiables.
- Facilitar futuras ampliaciones con nuevas tools.
"""

from __future__ import annotations

import ast
import math
import operator as op
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Any

import requests
from tavily import TavilyClient

from src.config.settings import TAVILY_API_KEY


# =========================
# FECHA Y HORA
# =========================
TIMEZONE_MAP = {
    "españa": "Europe/Madrid",
    "madrid": "Europe/Madrid",
    "china": "Asia/Shanghai",
    "pekín": "Asia/Shanghai",
    "beijing": "Asia/Shanghai",
    "shanghai": "Asia/Shanghai",
    "japón": "Asia/Tokyo",
    "tokio": "Asia/Tokyo",
    "reino unido": "Europe/London",
    "londres": "Europe/London",
    "méxico": "America/Mexico_City",
    "mexico": "America/Mexico_City",
    "argentina": "America/Argentina/Buenos_Aires",
    "buenos aires": "America/Argentina/Buenos_Aires",
    "colombia": "America/Bogota",
    "bogotá": "America/Bogota",
    "bogota": "America/Bogota",
    "estados unidos": "America/New_York",
    "nueva york": "America/New_York",
}

def get_current_datetime(location: str | None = None) -> str:
    """
    Devuelve la fecha y hora actual del sistema o de una ubicación conocida.
    """
    if location:
        normalized_location = location.strip().lower()
        timezone_name = TIMEZONE_MAP.get(normalized_location)

        if timezone_name:
            now = datetime.now(ZoneInfo(timezone_name))
            return (
                f"Fecha y hora actual en {location.title()}: "
                f"{now.strftime('%d/%m/%Y %H:%M:%S')}"
            )

        return (
            f"No tengo configurada la zona horaria para '{location}'. "
            "Prueba con un país o ciudad principal."
        )

    now = datetime.now()
    return now.strftime("Fecha y hora actual: %d/%m/%Y %H:%M:%S")

# =========================
# CALCULADORA 
# =========================

_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
}

_ALLOWED_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "round": round,
}


def _safe_eval(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Solo se permiten números.")

    if isinstance(node, ast.BinOp):
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        operator_type = type(node.op)

        if operator_type not in _ALLOWED_OPERATORS:
            raise ValueError("Operador no permitido.")

        return _ALLOWED_OPERATORS[operator_type](left, right)

    if isinstance(node, ast.UnaryOp):
        operand = _safe_eval(node.operand)
        operator_type = type(node.op)

        if operator_type not in _ALLOWED_OPERATORS:
            raise ValueError("Operador no permitido.")

        return _ALLOWED_OPERATORS[operator_type](operand)

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Función no permitida.")

        func_name = node.func.id
        if func_name not in _ALLOWED_FUNCTIONS:
            raise ValueError(f"Función no permitida: {func_name}")

        args = [_safe_eval(arg) for arg in node.args]
        return _ALLOWED_FUNCTIONS[func_name](*args)

    raise ValueError("Expresión no válida.")


def calculate_expression(expression: str) -> str:
    """
    Evalúa una expresión matemática simple de forma segura.
    """
    try:
        parsed = ast.parse(expression, mode="eval")
        result = _safe_eval(parsed.body)
        return f"Resultado: {result}"
    except Exception as e:
        return (
            f"No se pudo calcular la expresión '{expression}'. "
            f"Error: {e}"
        )


# =========================
# WEATHER TOOL 
# =========================

def _get_coordinates_from_city(city: str) -> tuple[float, float, str] | None:
    """
    Convierte una ciudad a coordenadas usando Open-Meteo Geocoding API.
    """
    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "es",
                "format": "json",
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        if not results:
            return None

        first = results[0]
        latitude = first["latitude"]
        longitude = first["longitude"]
        location_name = first["name"]
        country = first.get("country", "")

        display_name = f"{location_name}, {country}" if country else location_name
        return latitude, longitude, display_name

    except Exception:
        return None


def _format_date_spanish(date_str: str) -> str:
    """
    Convierte una fecha YYYY-MM-DD a formato:
    'lunes 6 de abril'
    """
    dt = datetime.strptime(date_str, "%Y-%m-%d")

    dias = [
        "lunes", "martes", "miércoles", "jueves",
        "viernes", "sábado", "domingo"
    ]

    meses = [
        "enero", "febrero", "marzo", "abril",
        "mayo", "junio", "julio", "agosto",
        "septiembre", "octubre", "noviembre", "diciembre"
    ]

    dia_semana = dias[dt.weekday()]
    mes = meses[dt.month - 1]

    return f"{dia_semana} {dt.day} de {mes}"

def _build_daily_lines(dates, weather_codes, temp_max, temp_min, precip, wind):
    lines = []

    for i in range(len(dates)):
        desc = _weather_code_to_spanish(weather_codes[i] if i < len(weather_codes) else None)
        tmax = temp_max[i] if i < len(temp_max) else "N/D"
        tmin = temp_min[i] if i < len(temp_min) else "N/D"
        rain = precip[i] if i < len(precip) else "N/D"
        w = wind[i] if i < len(wind) else "N/D"

        lines.append(
            f"- {_format_date_spanish(dates[i]).capitalize()}: "
            f"{desc}. Máxima {tmax} °C, mínima {tmin} °C, "
            f"probabilidad de lluvia {rain}%, viento máximo {w} km/h."
        )

    return lines


def _weather_code_to_spanish(code: int | None) -> str:
    """
    Traduce weather codes de Open-Meteo a español.
    """
    mapping = {
        0: "Despejado",
        1: "Principalmente despejado",
        2: "Parcialmente nuboso",
        3: "Cubierto",
        45: "Niebla",
        48: "Niebla con escarcha",
        51: "Llovizna ligera",
        53: "Llovizna moderada",
        55: "Llovizna intensa",
        56: "Llovizna helada ligera",
        57: "Llovizna helada intensa",
        61: "Lluvia ligera",
        63: "Lluvia moderada",
        65: "Lluvia intensa",
        66: "Lluvia helada ligera",
        67: "Lluvia helada intensa",
        71: "Nieve ligera",
        73: "Nieve moderada",
        75: "Nieve intensa",
        77: "Granos de nieve",
        80: "Chubascos ligeros",
        81: "Chubascos moderados",
        82: "Chubascos violentos",
        85: "Chubascos de nieve ligeros",
        86: "Chubascos de nieve intensos",
        95: "Tormenta",
        96: "Tormenta con granizo ligero",
        99: "Tormenta con granizo fuerte",
    }
    return mapping.get(code, f"Código meteorológico desconocido ({code})")

def get_weather(city: str, scope: str = "current") -> str:
    """
    Devuelve información meteorológica de una ciudad usando Open-Meteo.
    Scope soportado:
        - current
        - today
        - tomorrow
        - weekly
        - next_week
        - next_weekend
    """
    coordinates = _get_coordinates_from_city(city)

    if not coordinates:
        return f"No he podido encontrar la ubicación de '{city}'."

    latitude, longitude, display_name = coordinates

    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "wind_speed_10m",
                    "weather_code",
                ],
                "daily": [
                    "weather_code",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_probability_max",
                    "wind_speed_10m_max",
                ],
                "timezone": "auto",
                "forecast_days": 14,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        dates = daily.get("time", [])
        weather_codes = daily.get("weather_code", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_probability_max", [])
        wind = daily.get("wind_speed_10m_max", [])

        if scope == "current":
            if not current:
                return f"No he podido obtener el tiempo actual para {display_name}."

            return (
                f"Tiempo actual en {display_name}:\n"
                f"- Estado: {_weather_code_to_spanish(current.get('weather_code'))}\n"
                f"- Temperatura: {current.get('temperature_2m')} °C\n"
                f"- Sensación térmica: {current.get('apparent_temperature')} °C\n"
                f"- Humedad: {current.get('relative_humidity_2m')}%\n"
                f"- Viento: {current.get('wind_speed_10m')} km/h"
            )

        if scope == "today":
            if not dates:
                return f"No he podido obtener la previsión de hoy para {display_name}."

            return "\n".join(
                [f"Previsión para hoy en {display_name}:"]
                + _build_daily_lines(
                    dates[:1], weather_codes[:1], temp_max[:1], temp_min[:1], precip[:1], wind[:1]
                )
            )

        if scope == "tomorrow":
            if len(dates) < 2:
                return f"No he podido obtener la previsión de mañana para {display_name}."

            return "\n".join(
                [f"Previsión para mañana en {display_name}:"]
                + _build_daily_lines(
                    dates[1:2], weather_codes[1:2], temp_max[1:2], temp_min[1:2], precip[1:2], wind[1:2]
                )
            )

        if scope == "weekly":
            if not dates:
                return f"No he podido obtener la previsión semanal para {display_name}."

            return "\n".join(
                [f"Previsión meteorológica para los próximos 7 días en {display_name}:"]
                + _build_daily_lines(
                    dates[:7], weather_codes[:7], temp_max[:7], temp_min[:7], precip[:7], wind[:7]
                )
            )

        if scope == "next_week":
            if len(dates) < 14:
                return (
                    f"No dispongo de suficientes datos para calcular la semana siguiente completa en {display_name}. "
                    f"Estas son las previsiones disponibles de los próximos días:\n\n"
                    + "\n".join(
                        _build_daily_lines(
                            dates[:7], weather_codes[:7], temp_max[:7], temp_min[:7], precip[:7], wind[:7]
                        )
                    )
                )

            return "\n".join(
                [f"Previsión meteorológica para la siguiente semana en {display_name}:"]
                + _build_daily_lines(
                    dates[7:14], weather_codes[7:14], temp_max[7:14], temp_min[7:14], precip[7:14], wind[7:14]
                )
            )

        if scope == "next_weekend":
            if not dates:
                return f"No he podido obtener la previsión del próximo fin de semana para {display_name}."

            weekend_dates = []
            weekend_codes = []
            weekend_max = []
            weekend_min = []
            weekend_precip = []
            weekend_wind = []

            for i, date_str in enumerate(dates):
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if dt.weekday() in [5, 6]:  # sábado=5, domingo=6
                    weekend_dates.append(date_str)
                    weekend_codes.append(weather_codes[i])
                    weekend_max.append(temp_max[i])
                    weekend_min.append(temp_min[i])
                    weekend_precip.append(precip[i])
                    weekend_wind.append(wind[i])

                    if len(weekend_dates) == 2:
                        break

            if not weekend_dates:
                return f"No he podido identificar el próximo fin de semana para {display_name}."

            return "\n".join(
                [f"Previsión meteorológica para el próximo fin de semana en {display_name}:"]
                + _build_daily_lines(
                    weekend_dates, weekend_codes, weekend_max, weekend_min, weekend_precip, weekend_wind
                )
            )

        return f"No reconozco el alcance temporal '{scope}' para la consulta meteorológica."

    except Exception as e:
        return f"No se pudo consultar el tiempo para {display_name}. Error: {e}"


# =========================
# WEB SEARCH TOOL 
# =========================

def search_web(query: str) -> str:
    """
    Realiza una búsqueda web usando Tavily Search API.
    """
    if not TAVILY_API_KEY:
        return (
            "La búsqueda web no está configurada todavía. "
            "Falta definir TAVILY_API_KEY en el archivo .env."
        )

    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)

        result = client.search(
            query=query,
            topic="general",
            max_results=5,
            include_answer=True,
            search_depth="basic",
        )

        answer = result.get("answer")
        results = result.get("results", [])

        if answer:
            return f"Búsqueda web:\n{answer}"

        if not results:
            return f"No encontré resultados útiles para: {query}"

        formatted_results = []
        for idx, item in enumerate(results[:3], start=1):
            title = item.get("title", "Sin título")
            url = item.get("url", "")
            content = item.get("content", "")

            snippet = content[:220].strip()
            formatted_results.append(
                f"{idx}. {title}\n"
                f"   {snippet}\n"
                f"   Fuente: {url}"
            )

        return "He encontrado esto en internet:\n\n" + "\n\n".join(formatted_results)

    except Exception as e:
        return f"No se pudo realizar la búsqueda web. Error: {e}"