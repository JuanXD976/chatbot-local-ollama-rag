"use client";

import { useEffect, useRef } from "react";

type AttachmentComposerProps = {
  value: string;
  pending: boolean;
  selectedFiles: File[];
  onChange: (value: string) => void;
  onFilesChange: (files: File[]) => void;
  onSend: () => void;
};

export default function AttachmentComposer({
  value,
  pending,
  selectedFiles,
  onChange,
  onFilesChange,
  onSend,
}: AttachmentComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "0px";
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
  }, [value]);

  const removeFile = (index: number) => {
    onFilesChange(selectedFiles.filter((_, i) => i !== index));
  };

  return (
    <div className="input-shell" style={{ flexDirection: "column", alignItems: "stretch" }}>
      {selectedFiles.length > 0 && (
        <div className="selected-files-list">
          {selectedFiles.map((file, index) => (
            <div key={`${file.name}-${index}`} className="selected-file-item">
              <div className="selected-file-info">
                <strong>{file.name}</strong>
                <div className="small-muted">{(file.size / 1024).toFixed(2)} KB</div>
              </div>
              <button className="mini-remove-btn" onClick={() => removeFile(index)}>×</button>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: "flex", gap: 8, alignItems: "flex-end" }}>
        <button
          type="button"
          className="btn"
          onClick={() => fileInputRef.current?.click()}
          disabled={pending}
        >
          Adjuntar
        </button>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".txt,.md,.pdf,.docx,.xlsx,.csv,.png,.jpg,.jpeg,.webp"
          style={{ display: "none" }}
          onChange={(e) => {
            const files = Array.from(e.target.files || []);
            onFilesChange([...selectedFiles, ...files]);
          }}
        />

        <textarea
          ref={textareaRef}
          className="chat-input"
          placeholder="Escribe tu mensaje o adjunta archivos..."
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
          disabled={pending || (!value.trim() && selectedFiles.length === 0)}
          title={pending ? "Generando..." : "Enviar"}
        >
          ↑
        </button>
      </div>
    </div>
  );
}