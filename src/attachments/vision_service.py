from __future__ import annotations

import base64
import io

import requests
from PIL import Image

from src.config.settings import OLLAMA_BASE_URL, OLLAMA_VISION_MODEL
from src.core.exceptions import OllamaConnectionError
from src.core.system_prompt import build_base_system_prompt
from src.llm.ollama_client import clean_response
from src.utils.language import detect_language


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
    language = detect_language(user_prompt)

    messages = [
        {
            "role": "system",
            "content": (
                build_base_system_prompt(language)
                + "You are a precise visual assistant. "
                + "Analyze the image and describe only what is actually visible. "
                + "If the user asks about a technical error, try to identify it. "
                + "If there is visible text, include it if it is relevant. "
                + "Do not invent details that are not visible."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Visual file: {file_name}\n"
                f"User question: {user_prompt}\n\n"
                "Analyze the image and answer with the most useful information."
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
            f"Visual model {model_name} returned HTTP {response.status_code}. "
            f"Detail: {error_text}"
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
        "No available visual model could produce a response. "
        + " | ".join(errors)
    )