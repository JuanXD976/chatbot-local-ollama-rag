from __future__ import annotations

from lingua import Language, LanguageDetectorBuilder

SUPPORTED_LANGUAGES = [
    Language.ENGLISH,
    Language.SPANISH,
    Language.FRENCH,
    Language.GERMAN,
    Language.ITALIAN,
    Language.PORTUGUESE,
    Language.DUTCH,
    Language.POLISH,
    Language.ROMANIAN,
    Language.CATALAN,
    Language.CHINESE,
    Language.JAPANESE,
    Language.KOREAN,
    Language.RUSSIAN,
    Language.ARABIC,
    Language.HINDI,
    Language.BENGALI,
    Language.VIETNAMESE,
    Language.TURKISH,
]

_detector = LanguageDetectorBuilder.from_languages(*SUPPORTED_LANGUAGES).build()

LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "pl": "Polish",
    "ro": "Romanian",
    "ca": "Catalan",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ru": "Russian",
    "ar": "Arabic",
    "hi": "Hindi",
    "bn": "Bengali",
    "vi": "Vietnamese",
    "tr": "Turkish",
}


def detect_language(text: str) -> str:
    """
    Detecta el idioma principal del texto del usuario.
    Devuelve un código ISO-639-1 corto cuando sea posible.
    Fallback: 'en'
    """
    if not text or not text.strip():
        return "en"

    result = _detector.detect_language_of(text)
    if result is None:
        return "en"

    try:
        return result.iso_code_639_1.name.lower()
    except Exception:
        return "en"


def get_language_name(language_code: str) -> str:
    return LANGUAGE_NAMES.get(language_code, "the same language as the user")


def get_language_instruction(language_code: str) -> str:
    language_name = get_language_name(language_code)
    return (
        f"Respond in {language_name}. "
        "Do not switch languages unless the user explicitly asks for it."
    )