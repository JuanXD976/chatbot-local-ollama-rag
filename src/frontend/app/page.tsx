"use client";

import { useEffect, useRef, useState } from "react";
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
  uploadDocument,
  type DocumentItem,
  type SessionSummary,
} from "../lib/api";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
};

export default function HomePage() {
  const [health, setHealth] = useState<any>(null);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [docStatus, setDocStatus] = useState<any>(null);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [infoMessage, setInfoMessage] = useState<string>("");

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
  }

  async function handleDeleteSession(sessionId: string) {
    await deleteSession(sessionId);
    setInfoMessage("Sesión eliminada.");

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

  async function handleUpload() {
    if (!selectedFile) return;

    try {
      const result = await uploadDocument(selectedFile);
      setInfoMessage(
        `Documento subido e indexado correctamente. Chunks añadidos: ${result.indexed_chunks}`
      );
      setSelectedFile(null);
      await refreshDocuments();
    } catch (error: any) {
      setInfoMessage(error.message || "No se pudo subir e indexar el documento.");
    }
  }

  async function handleRebuild() {
    try {
      const result = await rebuildDocuments();
      setInfoMessage(`Reindexación completa realizada. Chunks indexados: ${result.total_chunks}`);
      await refreshDocuments();
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
      await refreshDocuments();
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
    el.style.height = `${Math.min(el.scrollHeight, 220)}px`;
  }

  function handleChatScroll() {
    const el = chatScrollRef.current;
    if (!el) return;

    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    shouldAutoScrollRef.current = distanceFromBottom < 120;
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
    async function init() {
      await refreshHealth();
      await refreshSessions();
      await refreshDocuments();
    }
    init();
  }, []);

  return (
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
                  <button
                    className="session-title-btn"
                    onClick={() => loadSession(session.session_id)}
                  >
                    <div className="session-title-text">{session.title}</div>
                  </button>

                  <div style={{ marginTop: 8 }}>
                    <button
                      className="btn btn-danger"
                      style={{ width: "100%" }}
                      onClick={() => handleDeleteSession(session.session_id)}
                    >
                      Eliminar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="block">
            <h2 className="section-title">Memoria</h2>
            <button className="btn" onClick={handleResetMemory}>
              Borrar memoria persistente
            </button>
          </div>

          <div className="block">
            <h2 className="section-title">Documentos RAG</h2>

            <div className="stack">
              <div className="small-muted">
                Documentos cargados: {docStatus?.document_count ?? 0}
              </div>
              <div className="small-muted">
                Chunks indexados: {docStatus?.indexed_chunks ?? 0}
              </div>
              <div className="small-muted">
                Base vectorial: {docStatus?.vectorstore_exists ? "Disponible" : "Pendiente"}
              </div>
            </div>

            <div className="divider" />

            <div className="file-upload-shell">
              <input
                id="rag-file-input"
                className="file-input-hidden"
                type="file"
                accept=".txt,.md,.pdf,.docx"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              />

              <label htmlFor="rag-file-input" className="file-upload-btn">
                Seleccionar archivo
              </label>

              <div className={`file-selected-name ${selectedFile ? "file-selected-active" : ""}`}>
                {selectedFile ? selectedFile.name : "Ningún archivo seleccionado"}
              </div>
            </div>

            <div className="divider" />

            <div className="stack">
              <button className="btn" onClick={handleUpload} disabled={!selectedFile}>
                Subir e indexar documento
              </button>

              <button className="btn" onClick={handleRebuild}>
                Reindexar todo
              </button>
            </div>

            <div className="divider" />

            <div className="stack">
              {documents.length === 0 && (
                <div className="empty-state">No hay documentos cargados.</div>
              )}

              {documents.map((doc) => (
                <div key={doc.name} className="doc-item">
                  <div className="stack">
                    <strong>{doc.name}</strong>
                    <div className="doc-meta">
                      {doc.suffix} · {(doc.size_bytes / 1024).toFixed(2)} KB · {doc.modified_at}
                    </div>
                    <button className="btn btn-danger" onClick={() => handleDeleteDocument(doc.name)}>
                      Eliminar
                    </button>
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
            <h1 className="page-title">🤖 Chatbot Local con Ollama - V2.0</h1>
            <p className="page-subtitle">
              Frontend premium con Next.js + backend FastAPI reutilizando tu core actual de IA.
            </p>
            <p className="small-muted" style={{ marginTop: 10 }}>
              Modelo local actual: {health?.model ?? "desconocido"}
            </p>
          </div>

          <div className={`status-card ${health?.ok ? "status-ok" : "status-error"}`}>
            {health?.ok ? "Ollama conectado correctamente." : "No se pudo conectar con Ollama."}
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
  );
}