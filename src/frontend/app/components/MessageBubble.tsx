"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type MessageBubbleProps = {
  role: "user" | "assistant";
  content: string;
  pending?: boolean;
  sources?: string[];
  attachments?: string[];
};

export default function MessageBubble({
  role,
  content,
  pending = false,
  sources = [],
  attachments = [],
}: MessageBubbleProps) {
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(content || "");
    } catch {
      // ignore
    }
  };

  return (
    <div className={`message-row ${role === "user" ? "message-row-user" : "message-row-assistant"}`}>
      <div className={`message ${role === "user" ? "message-user" : "message-assistant"}`}>
        {attachments.length > 0 && (
          <div className="sources-box" style={{ marginBottom: 10 }}>
            <div className="sources-title">Adjuntos</div>
            {attachments.map((a, i) => (
              <span key={i} className="source-chip">
                {a}
              </span>
            ))}
          </div>
        )}

        {content ? (
          role === "assistant" ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          ) : (
            content
          )
        ) : pending ? (
          <span className="assistant-thinking">Pensando...</span>
        ) : null}

        {sources.length > 0 && (
          <div className="sources-box">
            <div className="sources-title">Fuentes</div>
            {sources.map((s, i) => (
              <span key={i} className="source-chip">
                {s}
              </span>
            ))}
          </div>
        )}

        {role === "assistant" && content && !pending && (
          <div className="message-actions">
            <button className="copy-btn" onClick={copyToClipboard} title="Copiar respuesta">
              Copiar
            </button>
          </div>
        )}
      </div>
    </div>
  );
}