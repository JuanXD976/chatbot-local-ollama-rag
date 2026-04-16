"""
Configuración global de logging.

Motivo de su creación:
- Centralizar el formato y nivel de logs.
- Facilitar depuración y observabilidad.
"""

from __future__ import annotations

import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """
    Configura el logging global del proyecto.

    Args:
        level: Nivel de logging en texto (DEBUG, INFO, WARNING, ERROR).
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )