"use client";

import { useRef, useState } from "react";

type UploadDropzoneProps = {
  onUploadFiles: (files: File[]) => Promise<void>;
};

export default function UploadDropzone({ onUploadFiles }: UploadDropzoneProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);

  const addFiles = (incoming: File[]) => {
    if (incoming.length === 0) return;

    const deduped = [...selectedFiles];
    for (const file of incoming) {
      const exists = deduped.some(
        (f) => f.name === file.name && f.size === file.size && f.lastModified === file.lastModified
      );
      if (!exists) deduped.push(file);
    }
    setSelectedFiles(deduped);
  };

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0 || uploading) return;

    try {
      setUploading(true);
      await onUploadFiles(selectedFiles);
      setSelectedFiles([]);
      if (inputRef.current) inputRef.current.value = "";
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-zone-wrapper">
      <div
        className={`upload-zone ${isDragging ? "upload-zone-active" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={(e) => {
          e.preventDefault();
          setIsDragging(false);
        }}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          addFiles(Array.from(e.dataTransfer.files || []));
        }}
      >
        <div className="upload-zone-title">Arrastra archivos aquí</div>
        <div className="small-muted">o selecciónalos manualmente</div>

        <div style={{ marginTop: 10 }}>
          <button
            type="button"
            className="upload-btn"
            onClick={() => inputRef.current?.click()}
          >
            ⬆️ Cargar documentos
          </button>
        </div>

        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".txt,.md,.pdf,.docx"
          style={{ display: "none" }}
          onChange={(e) => addFiles(Array.from(e.target.files || []))}
        />
      </div>

      <div className="selected-files-list">
        {selectedFiles.length === 0 ? (
          <div className="small-muted">No hay archivos seleccionados.</div>
        ) : (
          selectedFiles.map((file, index) => (
            <div key={`${file.name}-${index}`} className="selected-file-item">
              <div className="selected-file-info">
                <strong>{file.name}</strong>
                <div className="small-muted">{(file.size / 1024).toFixed(2)} KB</div>
              </div>
              <button
                type="button"
                className="mini-remove-btn"
                onClick={() => removeFile(index)}
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>

      <button
        type="button"
        className="btn"
        disabled={selectedFiles.length === 0 || uploading}
        onClick={handleUpload}
      >
        {uploading ? "Subiendo..." : "Subir e indexar documentos"}
      </button>
    </div>
  );
}