"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import SessionList from "./components/SessionList";
import MessageBubble from "./components/MessageBubble";
import ChatComposer from "./components/ChatComposer";
import AdminPanel from "./components/AdminPanel";

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

  const chatScrollRef = useRef<HTMLDivElement | null>(null);
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

  async function handleUploadFiles(files: File[]) {
    try {
      const result = await uploadDocuments(files);

      const okResults = result.results.filter((r) => !r.error);
      const errorResults = result.results.filter((r) => r.error);

      if (okResults.length > 0 && errorResults.length === 0) {
        setInfoMessage(`Se subieron e indexaron ${okResults.length} documento(s) correctamente.`);
      } else if (okResults.length > 0 && errorResults.length > 0) {
        setInfoMessage(`Se subieron ${okResults.length} documento(s) correctamente y ${errorResults.length} fallaron.`);
      } else if (errorResults.length > 0) {
        setInfoMessage(`No se pudo subir ningún documento. Primer error: ${errorResults[0].error}`);
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
      setInfoMessage(`Documento eliminado correctamente. Chunks borrados del índice: ${result.deleted_chunks ?? 0}`);
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

  function handleChatScroll() {
    const el = chatScrollRef.current;
    if (!el) return;

    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    shouldAutoScrollRef.current = distanceFromBottom < 120;
  }

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
            <SessionList
              sessions={sessions}
              activeSessionId={activeSessionId}
              onCreate={handleNewSession}
              onLoad={loadSession}
              onDelete={handleDeleteSession}
            />
          </div>
        </aside>

        <main className="main">
          <div className="main-header">
            <div className="hero-card">
              <div className="hero-top">
                <div className="hero-left">
                  <h1 className="page-title">🤖 Chatbot Local con Ollama - V5.0</h1>
                  <p className="page-subtitle">
                    Frontend modular, subida múltiple con drag & drop y administración avanzada.
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
                  <MessageBubble
                    key={index}
                    role={message.role}
                    content={message.content}
                    pending={pending && index === messages.length - 1}
                  />
                ))}
              </div>
            </div>

            <div className="input-bar">
              <ChatComposer
                value={input}
                pending={pending}
                onChange={setInput}
                onSend={handleSend}
              />
            </div>
          </div>
        </main>
      </div>

      <AdminPanel
        open={isAdminOpen}
        onClose={() => setIsAdminOpen(false)}
        themeMode={themeMode}
        onApplyTheme={applyTheme}
        health={health}
        docStatus={docStatus}
        documents={documents}
        onResetMemory={handleResetMemory}
        onUploadFiles={handleUploadFiles}
        onDeleteDocument={handleDeleteDocument}
        onRebuild={handleRebuild}
      />
    </>
  );
}