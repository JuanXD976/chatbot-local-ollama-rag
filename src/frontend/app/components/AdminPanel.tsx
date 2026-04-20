"use client";

import { useEffect, useState } from "react";
import type { DocumentItem } from "../../lib/api";
import UploadDropzone from "./UploadDropzone";

type ThemeMode = "light" | "dark" | "auto";
type AdminTab = "theme" | "system" | "memory" | "rag";

type AdminPanelProps = {
  open: boolean;
  onClose: () => void;
  themeMode: ThemeMode;
  onApplyTheme: (mode: ThemeMode) => void;
  health: any;
  docStatus: any;
  documents: DocumentItem[];
  onResetMemory: () => Promise<void>;
  onUploadFiles: (files: File[]) => Promise<void>;
  onDeleteDocument: (filename: string) => Promise<void>;
  onRebuild: () => Promise<void>;
};

export default function AdminPanel({
  open,
  onClose,
  themeMode,
  onApplyTheme,
  health,
  docStatus,
  documents,
  onResetMemory,
  onUploadFiles,
  onDeleteDocument,
  onRebuild,
}: AdminPanelProps) {
  const [tab, setTab] = useState<AdminTab>("theme");
  const [openDocumentMenuName, setOpenDocumentMenuName] = useState<string | null>(null);

  useEffect(() => {
    function closeMenus() {
      setOpenDocumentMenuName(null);
    }

    window.addEventListener("click", closeMenus);
    return () => window.removeEventListener("click", closeMenus);
  }, []);

  if (!open) return null;

  return (
    <>
      <div className="overlay" onClick={onClose} />
      <aside className="admin-panel">
        <div className="admin-header">
          <div>
            <h2 className="admin-title">Administración</h2>
            <div className="small-muted">
              Ajustes, memoria, sistema y base documental.
            </div>
          </div>

          <button className="btn btn-icon" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="admin-tabs">
          <button className={`admin-tab ${tab === "theme" ? "active" : ""}`} onClick={() => setTab("theme")}>
            Tema
          </button>
          <button className={`admin-tab ${tab === "system" ? "active" : ""}`} onClick={() => setTab("system")}>
            Sistema
          </button>
          <button className={`admin-tab ${tab === "memory" ? "active" : ""}`} onClick={() => setTab("memory")}>
            Memoria
          </button>
          <button className={`admin-tab ${tab === "rag" ? "active" : ""}`} onClick={() => setTab("rag")}>
            RAG
          </button>
        </div>

        <div className="stack">
          {tab === "theme" && (
            <div className="block" style={{ marginBottom: 0 }}>
              <h3 className="section-title">Tema visual</h3>
              <div className="theme-options">
                <button
                  className={`theme-chip ${themeMode === "light" ? "active" : ""}`}
                  onClick={() => onApplyTheme("light")}
                >
                  Claro
                </button>
                <button
                  className={`theme-chip ${themeMode === "dark" ? "active" : ""}`}
                  onClick={() => onApplyTheme("dark")}
                >
                  Oscuro
                </button>
                <button
                  className={`theme-chip ${themeMode === "auto" ? "active" : ""}`}
                  onClick={() => onApplyTheme("auto")}
                >
                  Auto
                </button>
              </div>
            </div>
          )}

          {tab === "system" && (
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
          )}

          {tab === "memory" && (
            <div className="block" style={{ marginBottom: 0 }}>
              <h3 className="section-title">Memoria</h3>
              <button className="btn" onClick={onResetMemory}>
                Borrar memoria persistente
              </button>
            </div>
          )}

          {tab === "rag" && (
            <div className="block" style={{ marginBottom: 0 }}>
              <h3 className="section-title">Base documental RAG</h3>

              <div className="small-muted" style={{ marginBottom: 10 }}>
                Arrastra archivos o selecciónalos para subir varios a la vez.
              </div>

              <UploadDropzone onUploadFiles={onUploadFiles} />

              <div className="divider" />

              <button className="btn" onClick={onRebuild}>
                Reindexar todo
              </button>

              <div className="divider" />

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
                            setOpenDocumentMenuName((prev) =>
                              prev === doc.name ? null : doc.name
                            );
                          }}
                          title="Opciones"
                        >
                          ⋯
                        </button>

                        {openDocumentMenuName === doc.name && (
                          <div className="context-menu" onClick={(e) => e.stopPropagation()}>
                            <button
                              className="context-menu-item danger"
                              onClick={() => onDeleteDocument(doc.name)}
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
            </div>
          )}
        </div>
      </aside>
    </>
  );
}