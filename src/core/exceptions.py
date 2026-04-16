"""
Excepciones propias del proyecto.

Motivo de su creación:
- Centralizar errores conocidos.
- Mejorar trazabilidad y mantenimiento.
"""


class ChatbotError(Exception):
    """
    Excepción base del proyecto.
    """


class ConfigurationError(ChatbotError):
    """
    Error de configuración.
    """


class OllamaConnectionError(ChatbotError):
    """
    Error de conexión con Ollama.
    """


class ToolExecutionError(ChatbotError):
    """
    Error al ejecutar una tool.
    """


class RAGError(ChatbotError):
    """
    Error en la capa RAG.
    """


class SessionError(ChatbotError):
    """
    Error relacionado con sesiones conversacionales.
    """