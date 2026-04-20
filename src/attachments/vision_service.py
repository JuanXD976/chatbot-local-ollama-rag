from __future__ import annotations

import base64
import io

import requests
from PIL import Image

from src.config.settings import OLLAMA_BASE_URL, OLLAMA_VISION_MODEL
from src.core.exceptions import OllamaConnectionError
from src.llm.ollama_client import clean_response


MAX_IMAGE_SIDE = 1600
JPEG_QUALITY = 85
VISION_FALLBACK_MODELS = ["gemma3:4b", "gemma3:4"]


def _prepare_image_for_ollama(file_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")

    width, height = image.size
    longest_side = max(width, height)

    if longest_side > MAX_IMAGE_SIDE:
        scale = MAX_IMAGE_SIDE / longest_side
        new_size = (int(width * scale), int(height * scale))
        image = image.resize(new_size)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _call_vision_model(model_name: str, file_name: str, encoded: str, user_prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "Eres un asistente visual preciso. "
                "Analiza la imagen y describe solo lo que realmente se observa. "
                "Si el usuario pregunta por un error técnico, intenta identificarlo. "
                "Si hay texto visible, intégralo si es relevante. "
                "No inventes detalles no visibles. "
                "Responde en español."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Archivo visual: {file_name}\n"
                f"Pregunta del usuario: {user_prompt}\n\n"
                "Analiza la imagen y responde con la información útil."
            ),
            "images": [encoded],
        },
    ]

    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 700,
        },
    }

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json=payload,
        timeout=240,
    )

    if not response.ok:
        error_text = response.text[:1200]
        raise OllamaConnectionError(
            f"El modelo visual {model_name} devolvió error HTTP {response.status_code}. "
            f"Detalle: {error_text}"
        )

    data = response.json()
    content = data.get("message", {}).get("content", "")
    return clean_response(content)


def analyze_image_with_vision(
    file_name: str,
    file_bytes: bytes,
    user_prompt: str,
) -> str:
    encoded = _prepare_image_for_ollama(file_bytes)

    models_to_try = [OLLAMA_VISION_MODEL] + [
        model for model in VISION_FALLBACK_MODELS if model != OLLAMA_VISION_MODEL
    ]

    errors: list[str] = []

    for model_name in models_to_try:
        try:
            return _call_vision_model(model_name, file_name, encoded, user_prompt)
        except Exception as exc:
            errors.append(f"{model_name}: {exc}")

    raise OllamaConnectionError(
        "No se pudo obtener respuesta de ningún modelo visual disponible. "
        + " | ".join(errors)
    )