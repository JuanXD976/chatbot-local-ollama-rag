"use client";

import { useEffect, useState } from "react";
import type { SessionSummary } from "../../lib/api";

type SessionListProps = {
  sessions: SessionSummary[];
  activeSessionId: string | null;
  onCreate: () => void;
  onLoad: (sessionId: string) => void;
  onDelete: (sessionId: string) => void;
};

export default function SessionList({
  sessions,
  activeSessionId,
  onCreate,
  onLoad,
  onDelete,
}: SessionListProps) {
  const [openSessionMenuId, setOpenSessionMenuId] = useState<string | null>(null);

  useEffect(() => {
    function closeMenus() {
      setOpenSessionMenuId(null);
    }

    window.addEventListener("click", closeMenus);
    return () => window.removeEventListener("click", closeMenus);
  }, []);

  return (
    <div className="block">
      <h2 className="section-title">Sesiones</h2>

      <div className="stack">
        <button className="btn btn-primary" onClick={onCreate}>
          Nueva conversación
        </button>

        {sessions.length === 0 && (
          <div className="empty-state">Todavía no hay sesiones.</div>
        )}

        {sessions.map((session) => (
          <div
            key={session.session_id}
            className={`session-item ${activeSessionId === session.session_id ? "session-active" : ""}`}
          >
            <div className="item-top-row">
              <button
                className="session-title-btn"
                onClick={() => onLoad(session.session_id)}
              >
                <div className="session-title-text">{session.title}</div>
              </button>

              <div className="menu-wrapper">
                <button
                  className="menu-trigger"
                  onClick={(e) => {
                    e.stopPropagation();
                    setOpenSessionMenuId((prev) =>
                      prev === session.session_id ? null : session.session_id
                    );
                  }}
                  title="Opciones"
                >
                  ⋯
                </button>

                {openSessionMenuId === session.session_id && (
                  <div className="context-menu" onClick={(e) => e.stopPropagation()}>
                    <button
                      className="context-menu-item danger"
                      onClick={() => onDelete(session.session_id)}
                    >
                      Eliminar sesión
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}