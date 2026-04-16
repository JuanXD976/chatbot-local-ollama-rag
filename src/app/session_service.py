"""
Servicio de sesiones conversacionales.

Motivo de su creación:
- Gestionar sesiones independientes de la memoria persistente general.
- Permitir recuperación y persistencia por conversación.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from src.core.exceptions import SessionError
from src.core.models import ChatMessage, ChatSession


class SessionService:
    """
    Gestiona sesiones de conversación persistidas en JSON.
    """

    def __init__(self, storage_path: str) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        if not self.storage_path.exists():
            self.storage_path.write_text("{}", encoding="utf-8")

    def _load_sessions(self) -> Dict[str, dict]:
        try:
            content = self.storage_path.read_text(encoding="utf-8").strip()
            return json.loads(content) if content else {}
        except json.JSONDecodeError as exc:
            raise SessionError("El archivo de sesiones no contiene un JSON válido.") from exc

    def _save_sessions(self, sessions: Dict[str, dict]) -> None:
        self.storage_path.write_text(
            json.dumps(sessions, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def create_session(self, title: str = "Nueva conversación") -> ChatSession:
        session_id = str(uuid.uuid4())
        session = ChatSession(session_id=session_id, title=title)

        sessions = self._load_sessions()
        sessions[session_id] = asdict(session)
        self._save_sessions(sessions)

        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        sessions = self._load_sessions()
        data = sessions.get(session_id)

        if not data:
            return None

        messages = [ChatMessage(**msg) for msg in data.get("messages", [])]

        return ChatSession(
            session_id=data["session_id"],
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            messages=messages,
        )

    def list_sessions(self) -> List[ChatSession]:
        sessions = self._load_sessions()
        result: List[ChatSession] = []

        for data in sessions.values():
            messages = [ChatMessage(**msg) for msg in data.get("messages", [])]
            result.append(
                ChatSession(
                    session_id=data["session_id"],
                    title=data["title"],
                    created_at=data["created_at"],
                    updated_at=data["updated_at"],
                    messages=messages,
                )
            )

        return sorted(result, key=lambda x: x.updated_at, reverse=True)

    def append_message(self, session_id: str, role: str, content: str) -> None:
        sessions = self._load_sessions()

        if session_id not in sessions:
            raise SessionError(f"No existe la sesión '{session_id}'.")

        message = ChatMessage(role=role, content=content)
        sessions[session_id]["messages"].append(asdict(message))
        sessions[session_id]["updated_at"] = datetime.now(timezone.utc).isoformat()

        if sessions[session_id]["title"] == "Nueva conversación" and role == "user":
            sessions[session_id]["title"] = content[:50].strip() or "Nueva conversación"

        self._save_sessions(sessions)

    def delete_session(self, session_id: str) -> None:
        sessions = self._load_sessions()
        if session_id in sessions:
            del sessions[session_id]
            self._save_sessions(sessions)