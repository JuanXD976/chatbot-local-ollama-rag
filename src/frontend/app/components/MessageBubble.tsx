"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type MessageBubbleProps = {
  role: "user" | "assistant";
  content: string;
  pending?: boolean;
  sources?: string[];
  attachments?: string[];
  modeUsed?: string | null;
  outputFormatUsed?: string | null;
};

function getFirstCodeBlock(text: string): string | null {
  const match = text.match(/```(?:\w+)?\n([\s\S]*?)```/);
  return match ? match[1].trim() : null;
}

function getFirstMarkdownTable(text: string): string | null {
  const lines = text.split("\n");
  const tableLines: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (/\|/.test(line)) {
      tableLines.push(line);

      let j = i + 1;
      while (j < lines.length && /\|/.test(lines[j])) {
        tableLines.push(lines[j]);
        j++;
      }

      if (tableLines.length >= 2) {
        return tableLines.join("\n").trim();
      }

      tableLines.length = 0;
    }
  }

  return null;
}

function detectRealRenderedFormat(content: string): string | null {
  const text = content || "";

  const hasCodeFence = /```[\s\S]*?```/.test(text);
  const hasMarkdownTable =
    /\|.+\|/.test(text) && /\|(?:\s*-+\s*\|)+/.test(text);
  const hasList =
    /^\s*[-*]\s+/m.test(text) || /^\s*\d+\.\s+/m.test(text);

  if (hasCodeFence) return "codigo";
  if (hasMarkdownTable) return "tabla";
  if (hasList) return "puntos";
  return null;
}

function sanitizeVisibleContent(text: string): string {
  if (!text) return "";

  let cleaned = text.trimStart();

  cleaned = cleaned.replace(/^\s*Formato:\s*(tabla|puntos|codigo|normal)\s*\n*/i, "");
  cleaned = cleaned.replace(/^\s*Modo:\s*(auto|analista|programador|resumidor)\s*\n*/i, "");

  return cleaned;
}

function extractCodeLanguage(className?: string): string {
  if (!className) return "Código";
  const match = className.match(/language-(\w+)/);
  if (!match) return "Código";

  const lang = match[1].toLowerCase();
  if (lang === "ts" || lang === "tsx") return "TypeScript";
  if (lang === "js" || lang === "jsx") return "JavaScript";
  if (lang === "py") return "Python";
  return lang.charAt(0).toUpperCase() + lang.slice(1);
}

export default function MessageBubble({
  role,
  content,
  pending = false,
  sources = [],
  attachments = [],
  modeUsed = null,
  outputFormatUsed = null,
}: MessageBubbleProps) {
  const visibleContent = sanitizeVisibleContent(content);

  const realFormat = role === "assistant" ? detectRealRenderedFormat(visibleContent) : null;
  const visibleFormat =
    realFormat === "codigo" || realFormat === "tabla" ? realFormat : null;

  const codeOnly = getFirstCodeBlock(visibleContent);
  const tableOnly = getFirstMarkdownTable(visibleContent);

  let copyLabel = "Copiar";
  let copyPayload = visibleContent || "";

  if (codeOnly) {
    copyLabel = "Copiar código";
    copyPayload = codeOnly;
  } else if (tableOnly) {
    copyLabel = "Copiar tabla";
    copyPayload = tableOnly;
  }

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(copyPayload);
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
              <span key={i} className="source-chip">{a}</span>
            ))}
          </div>
        )}

        {role === "assistant" && (modeUsed || visibleFormat) && (
          <div className="message-meta-row">
            {modeUsed && <span className="message-mode-badge">Modo: {modeUsed}</span>}
          </div>
        )}

        {visibleContent ? (
          role === "assistant" ? (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ className, children, ...props }: any) {
                  const text = String(children).replace(/\n$/, "");
                  const isBlock = Boolean(className) || text.includes("\n");

                  if (!isBlock) {
                    return (
                      <code className="inline-code" {...props}>
                        {text}
                      </code>
                    );
                  }

                  const languageLabel = extractCodeLanguage(className);

                  return (
                    <div className="code-block-shell">
                      <div className="code-block-header">
                        <div className="code-block-title">{languageLabel}</div>
                        <button
                          className="code-copy-btn"
                          onClick={async () => {
                            try {
                              await navigator.clipboard.writeText(text);
                            } catch {
                              // ignore
                            }
                          }}
                          title="Copiar código"
                          type="button"
                        >
                          Copiar
                        </button>
                      </div>
                      <pre className="code-block-pre">
                        <code className={className} {...props}>
                          {text}
                        </code>
                      </pre>
                    </div>
                  );
                },
              }}
            >
              {visibleContent}
            </ReactMarkdown>
          ) : (
            visibleContent
          )
        ) : pending ? (
          <span className="assistant-thinking">Pensando...</span>
        ) : null}

        {sources.length > 0 && (
          <div className="sources-box">
            <div className="sources-title">Fuentes</div>
            {sources.map((s, i) => (
              <span key={i} className="source-chip">{s}</span>
            ))}
          </div>
        )}

        {role === "assistant" && visibleContent && !pending && !codeOnly && (
          <div className="message-actions">
            <button className="copy-btn" onClick={copyToClipboard} title={copyLabel}>
              {copyLabel}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}