"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import UploadButton from "./components/UploadButton";

import {
  chatStream,
  createSession,
  deleteDocument,
  deleteSession,
  getSession,
  healthCheck,
  listDocuments,
  listSessions,
  rebuildDocuments,
  resetMemory,
  uploadDocuments,
  type DocumentItem,
  type SessionSummary,
} from "../lib/api";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
};

type ThemeMode = "light" | "dark" | "auto";

export default function HomePage() {
  const [health, setHealth] = useState<any>(null);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [docStatus, setDocStatus] = useState<any>(null);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const [infoMessage, setInfoMessage] = useState<string>("");
  const [isAdminOpen, setIsAdminOpen] = useState(false);
  const [themeMode, setThemeMode] = useState<ThemeMode>("light");
  const [openSessionMenuId, setOpenSessionMenuId] = useState<string | null>(null);
  const [openDocumentMenuName, setOpenDocumentMenuName] = useState<string | null>(null);

  const chatScrollRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const shouldAutoScrollRef = useRef(true);

  async function refreshHealth() {
    const data = await healthCheck();
    setHealth(data);
  }

  async function refreshSessions() {
    const data = await listSessions();
    setSessions(data);

    if (!activeSessionId && data.length > 0) {
      setActiveSessionId(data[0].session_id);
      await loadSession(data[0].session_id);
    }
  }

  async function refreshDocuments() {
    const data = await listDocuments();
    setDocuments(data.documents);
    setDocStatus(data.status);
  }

  async function loadSession(sessionId: string) {
    const session = await getSession(sessionId);
    setActiveSessionId(sessionId);
    setMessages(
      session.messages.map((m) => ({
        role: m.role as "user" | "assistant",
        content: m.content,
        timestamp: m.timestamp,
      }))
    );
    setInfoMessage("");
    setOpenSessionMenuId(null);

    requestAnimationFrame(() => {
      if (chatScrollRef.current) {
        chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
      }
    });
  }

  async function handleNewSession() {
    const session = await createSession();
    await refreshSessions();
    setActiveSessionId(session.session_id);
    setMessages([]);
    setInfoMessage("");
    setOpenSessionMenuId(null);
  }

  async function handleDeleteSession(sessionId: string) {
    await deleteSession(sessionId);
    setInfoMessage("Sesión eliminada.");
    setOpenSessionMenuId(null);

    const updated = await listSessions();
    setSessions(updated);

    if (activeSessionId === sessionId) {
      if (updated.length > 0) {
        setActiveSessionId(updated[0].session_id);
        await loadSession(updated[0].session_id);
      } else {
        const newSession = await createSession();
        setActiveSessionId(newSession.session_id);
        setMessages([]);
        await refreshSessions();
      }
    }
  }

  async function handleUploadFiles(files: File[]) {
    try {
      const result = await uploadDocuments(files);

      const okResults = result.results.filter((r) => !r.error);
      const errorResults = result.results.filter((r) => r.error);

      if (okResults.length > 0 && errorResults.length === 0) {
        setInfoMessage(
          `Se subieron e indexaron ${okResults.length} documento(s) correctamente.`
        );
      } else if (okResults.length > 0 && errorResults.length > 0) {
        setInfoMessage(
          `Se subieron ${okResults.length} documento(s) correctamente y ${errorResults.length} fallaron.`
        );
      } else if (errorResults.length > 0) {
        setInfoMessage(
          `No se pudo subir ningún documento. Primer error: ${errorResults[0].error}`
        );
      }

      await refreshDocuments();
      await refreshHealth();
    } catch (error: any) {
      setInfoMessage(error.message || "No se pudieron subir los documentos.");
    }
  }

  async function handleRebuild() {
    try {
      const result = await rebuildDocuments();
      setInfoMessage(`Reindexación completa realizada. Chunks indexados: ${result.total_chunks}`);
      await refreshDocuments();
      await refreshHealth();
    } catch (error: any) {
      setInfoMessage(error.message || "No se pudo reindexar la base vectorial.");
    }
  }

  async function handleDeleteDocument(filename: string) {
    try {
      const result = await deleteDocument(filename);
      setInfoMessage(
        `Documento eliminado correctamente. Chunks borrados del índice: ${result.deleted_chunks ?? 0}`
      );
      setOpenDocumentMenuName(null);
      await refreshDocuments();
      await refreshHealth();
    } catch (error: any) {
      setInfoMessage(error.message || "No se pudo eliminar el documento.");
    }
  }

  async function handleResetMemory() {
    await resetMemory();
    setInfoMessage("Memoria persistente borrada correctamente.");
  }

  async function handleSend() {
    if (!input.trim() || pending) return;

    let sessionId = activeSessionId;
    if (!sessionId) {
      const session = await createSession();
      sessionId = session.session_id;
      setActiveSessionId(sessionId);
      await refreshSessions();
    }

    const userMessage = input.trim();
    setInput("");
    setPending(true);
    setInfoMessage("");
    shouldAutoScrollRef.current = true;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: userMessage, timestamp: new Date().toISOString() },
      { role: "assistant", content: "", timestamp: new Date().toISOString() },
    ]);

    try {
      const result = await chatStream(userMessage, sessionId, (chunk) => {
        setMessages((prev) => {
          const next = [...prev];
          const lastIndex = next.length - 1;
          next[lastIndex] = {
            ...next[lastIndex],
            content: next[lastIndex].content + chunk,
          };
          return next;
        });
      });

      if (result.sessionId && result.sessionId !== activeSessionId) {
        setActiveSessionId(result.sessionId);
      }

      await refreshSessions();
    } catch (error: any) {
      setMessages((prev) => {
        const next = [...prev];
        const lastIndex = next.length - 1;
        next[lastIndex] = {
          role: "assistant",
          content: error.message || "Error al generar la respuesta.",
          timestamp: new Date().toISOString(),
        };
        return next;
      });
    } finally {
      setPending(false);
    }
  }

  function handleTextareaKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function autoResizeTextarea() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "0px";
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
  }

  function handleChatScroll() {
    const el = chatScrollRef.current;
    if (!el) return;

    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    shouldAutoScrollRef.current = distanceFromBottom < 120;
  }

  function applyTheme(mode: ThemeMode) {
    setThemeMode(mode);
    localStorage.setItem("chatbot_theme_mode", mode);

    const html = document.documentElement;

    if (mode === "auto") {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      html.setAttribute("data-theme", prefersDark ? "dark" : "light");
      return;
    }

    html.setAttribute("data-theme", mode);
  }

  function toggleSessionMenu(sessionId: string) {
    setOpenSessionMenuId((prev) => (prev === sessionId ? null : sessionId));
  }

  function toggleDocumentMenu(docName: string) {
    setOpenDocumentMenuName((prev) => (prev === docName ? null : docName));
  }

  useEffect(() => {
    autoResizeTextarea();
  }, [input]);

  useEffect(() => {
    if (!chatScrollRef.current) return;
    if (shouldAutoScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [messages, pending]);

  useEffect(() => {
    const saved = localStorage.getItem("chatbot_theme_mode") as ThemeMode | null;
    const initial = saved || "light";
    applyTheme(initial);
  }, []);

  useEffect(() => {
    async function init() {
      await refreshHealth();
      await refreshSessions();
      await refreshDocuments();
    }
    init();
  }, []);

  useEffect(() => {
    function handleGlobalClick() {
      setOpenSessionMenuId(null);
      setOpenDocumentMenuName(null);
    }

    window.addEventListener("click", handleGlobalClick);
    return () => window.removeEventListener("click", handleGlobalClick);
  }, []);

  const systemStatusText = useMemo(() => {
    if (!health) return "Comprobando estado del sistema...";
    if (!health.ok) return "No se pudo conectar con Ollama.";
    return "Ollama conectado correctamente.";
  }, [health]);

  return (
    <>
      <div className="app-shell">
        <aside className="sidebar">
          <div className="sidebar-scroll">
            <div className="block">
              <h2 className="section-title">Sesiones</h2>

              <div className="stack">
                <button className="btn btn-primary" onClick={handleNewSession}>
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
                        onClick={() => loadSession(session.session_id)}
                      >
                        <div className="session-title-text">{session.title}</div>
                      </button>

                      <div className="menu-wrapper">
                        <button
                          className="menu-trigger"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleSessionMenu(session.session_id);
                          }}
                          title="Opciones"
                        >
                          ⋯
                        </button>

                        {openSessionMenuId === session.session_id && (
                          <div
                            className="context-menu"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <button
                              className="context-menu-item danger"
                              onClick={() => handleDeleteSession(session.session_id)}
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
          </div>
        </aside>

        <main className="main">
          <div className="main-header">
            <div className="hero-card">
              <div className="hero-top">
                <div className="hero-left">
                  <h1 className="page-title">🤖 Chatbot Local con Ollama - V3.0</h1>
                  <p className="page-subtitle">
                    Experiencia premium con Next.js + FastAPI, memoria persistente y administración RAG.
                  </p>
                  <p className="small-muted" style={{ marginTop: 8 }}>
                    Modelo local actual: {health?.model ?? "desconocido"}
                  </p>
                </div>

                <div className="top-actions">
                  <div className="theme-pill">
                    Tema: {themeMode === "light" ? "Claro" : themeMode === "dark" ? "Oscuro" : "Auto"}
                  </div>
                  <button
                    className="btn btn-icon"
                    onClick={() => setIsAdminOpen(true)}
                    title="Abrir administración"
                  >
                    ⋯
                  </button>
                </div>
              </div>
            </div>

            <div className={`status-card ${health?.ok ? "status-ok" : "status-error"}`}>
              {systemStatusText}
            </div>
          </div>

          <div className="main-body">
            <div className="chat-scroll" ref={chatScrollRef} onScroll={handleChatScroll}>
              {infoMessage && <div className="info-banner">{infoMessage}</div>}

              <div className="chat-window">
                {messages.length === 0 && (
                  <div className="empty-state">
                    Empieza una conversación o carga una sesión existente.
                  </div>
                )}

                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`message-row ${
                      message.role === "user" ? "message-row-user" : "message-row-assistant"
                    }`}
                  >
                    <div
                      className={`message ${
                        message.role === "user" ? "message-user" : "message-assistant"
                      }`}
                    >
                      {message.content ? (
                        message.role === "assistant" ? (
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {message.content}
                          </ReactMarkdown>
                        ) : (
                          message.content
                        )
                      ) : pending && index === messages.length - 1 ? (
                        <span className="assistant-thinking">Pensando...</span>
                      ) : (
                        ""
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="input-bar">
              <div className="input-shell">
                <textarea
                  ref={textareaRef}
                  className="chat-input"
                  placeholder="Escribe tu mensaje..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleTextareaKeyDown}
                  rows={1}
                />
                <button
                  className="send-btn"
                  onClick={handleSend}
                  disabled={pending || !input.trim()}
                  title={pending ? "Generando..." : "Enviar"}
                >
                  ↑
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>

      {isAdminOpen && (
        <>
          <div className="overlay" onClick={() => setIsAdminOpen(false)} />
          <aside className="admin-panel">
            <div className="admin-header">
              <div>
                <h2 className="admin-title">Administración</h2>
                <div className="small-muted">
                  Gestiona memoria, documentos RAG y apariencia visual.
                </div>
              </div>

              <button className="btn btn-icon" onClick={() => setIsAdminOpen(false)}>
                ×
              </button>
            </div>

            <div className="stack">
              <div className="block" style={{ marginBottom: 0 }}>
                <h3 className="section-title">Tema visual</h3>
                <div className="theme-options">
                  <button
                    className={`theme-chip ${themeMode === "light" ? "active" : ""}`}
                    onClick={() => applyTheme("light")}
                  >
                    Claro
                  </button>
                  <button
                    className={`theme-chip ${themeMode === "dark" ? "active" : ""}`}
                    onClick={() => applyTheme("dark")}
                  >
                    Oscuro
                  </button>
                  <button
                    className={`theme-chip ${themeMode === "auto" ? "active" : ""}`}
                    onClick={() => applyTheme("auto")}
                  >
                    Auto
                  </button>
                </div>
              </div>

              <div className="block" style={{ marginBottom: 0 }}>
                <h3 className="section-title">Estado del sistema</h3>
                <div className="grid-two">
                  <div className="stat-card">
                    <strong>Modelo</strong>
                    <div className="small-muted" style={{ marginTop: 6 }}>
                      {health?.model ?? "desconocido"}
                    </div>
                  </div>
                  <div className="stat-card">
                    <strong>Conexión</strong>
                    <div className="small-muted" style={{ marginTop: 6 }}>
                      {health?.ok ? "Operativa" : "Con incidencias"}
                    </div>
                  </div>
                  <div className="stat-card">
                    <strong>Documentos</strong>
                    <div className="small-muted" style={{ marginTop: 6 }}>
                      {docStatus?.document_count ?? 0}
                    </div>
                  </div>
                  <div className="stat-card">
                    <strong>Chunks</strong>
                    <div className="small-muted" style={{ marginTop: 6 }}>
                      {docStatus?.indexed_chunks ?? 0}
                    </div>
                  </div>
                </div>
              </div>

              <div className="block" style={{ marginBottom: 0 }}>
                <h3 className="section-title">Memoria</h3>
                <div className="stack">
                  <button className="btn" onClick={handleResetMemory}>
                    Borrar memoria persistente
                  </button>
                </div>
              </div>

              <div className="block" style={{ marginBottom: 0 }}>
                <h3 className="section-title">Base documental RAG</h3>

                <div className="small-muted" style={{ marginBottom: 10 }}>
                  Sube, indexa, elimina o reindexa documentos del sistema.
                </div>

                <div className="stack">
                  {documents.length === 0 && (
                    <div className="empty-state">No hay documentos cargados.</div>
                  )}

                  {documents.map((doc) => (
                    <div key={doc.name} className="doc-item">
                      <div className="item-top-row">
                        <div className="doc-main-info">
                          <strong>{doc.name}</strong>
                          <div className="doc-meta">
                            {doc.suffix} · {(doc.size_bytes / 1024).toFixed(2)} KB · {doc.modified_at}
                          </div>
                        </div>

                        <div className="menu-wrapper">
                          <button
                            className="menu-trigger"
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleDocumentMenu(doc.name);
                            }}
                            title="Opciones"
                          >
                            ⋯
                          </button>

                          {openDocumentMenuName === doc.name && (
                            <div
                              className="context-menu"
                              onClick={(e) => e.stopPropagation()}
                            >
                              <button
                                className="context-menu-item danger"
                                onClick={() => handleDeleteDocument(doc.name)}
                              >
                                Eliminar documento
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="divider" />

                <UploadButton onUpload={handleUploadFiles} />

                <div className="small-muted" style={{ marginTop: 8 }}>
                  Puedes seleccionar y subir varios documentos a la vez.
                </div>

                <div className="divider" />

                <button className="btn" onClick={handleRebuild}>
                  Reindexar todo
                </button>
              </div>
            </div>
          </aside>
        </>
      )}
    </>
  );
}