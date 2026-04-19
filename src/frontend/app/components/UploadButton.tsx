import { useRef } from "react";

type UploadButtonProps = {
  onUpload: (files: File[]) => void;
};

export default function UploadButton({ onUpload }: UploadButtonProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    onUpload(Array.from(files));
  };

  return (
    <div className="upload-wrapper">
      <button
        type="button"
        className="upload-btn"
        onClick={() => inputRef.current?.click()}
      >
        ⬆️ Cargar documentos
      </button>

      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".txt,.md,.pdf,.docx"
        style={{ display: "none" }}
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  );
}