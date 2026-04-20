import { useEffect, useRef } from "react";

type ChatComposerProps = {
  value: string;
  pending: boolean;
  onChange: (value: string) => void;
  onSend: () => void;
};

export default function ChatComposer({
  value,
  pending,
  onChange,
  onSend,
}: ChatComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;

    el.style.height = "0px";
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
  }, [value]);

  return (
    <div className="input-shell">
      <textarea
        ref={textareaRef}
        className="chat-input"
        placeholder="Escribe tu mensaje..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            onSend();
          }
        }}
        rows={1}
      />
      <button
        className="send-btn"
        onClick={onSend}
        disabled={pending || !value.trim()}
        title={pending ? "Generando..." : "Enviar"}
      >
        ↑
      </button>
    </div>
  );
}