const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type SessionSummary = {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type SessionMessage = {
  role: string;
  content: string;
  timestamp: string;
};

export type SessionDetail = {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: SessionMessage[];
};

export type DocumentItem = {
  name: string;
  path: string;
  size_bytes: number;
  suffix: string;
  modified_at: string;
};

export type UploadBatchResult = {
  file: string;
  indexed_chunks?: number;
  saved_path?: string;
  error?: string;
};

export type UploadBatchResponse = {
  results: UploadBatchResult[];
};

export async function healthCheck() {
  const res = await fetch(`${API_URL}/health`, { cache: "no-store" });
  if (!res.ok) throw new Error("No se pudo consultar el estado del backend.");
  return res.json();
}

export async function listSessions(): Promise<SessionSummary[]> {
  const res = await fetch(`${API_URL}/sessions`, { cache: "no-store" });
  if (!res.ok) throw new Error("No se pudieron cargar las sesiones.");
  return res.json();
}

export async function createSession(): Promise<SessionSummary> {
  const res = await fetch(`${API_URL}/sessions`, { method: "POST" });
  if (!res.ok) throw new Error("No se pudo crear la sesión.");
  return res.json();
}

export async function getSession(sessionId: string): Promise<SessionDetail> {
  const res = await fetch(`${API_URL}/sessions/${sessionId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("No se pudo cargar la sesión.");
  return res.json();
}

export async function deleteSession(sessionId: string) {
  const res = await fetch(`${API_URL}/sessions/${sessionId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("No se pudo eliminar la sesión.");
  return res.json();
}

export async function listDocuments() {
  const res = await fetch(`${API_URL}/documents`, { cache: "no-store" });
  if (!res.ok) throw new Error("No se pudieron cargar los documentos.");
  return res.json();
}

export async function uploadDocuments(files: File[]): Promise<UploadBatchResponse> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const res = await fetch(`${API_URL}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "No se pudieron subir los documentos.");
  }

  return res.json();
}

export async function rebuildDocuments() {
  const res = await fetch(`${API_URL}/documents/rebuild`, { method: "POST" });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "No se pudo reindexar la base vectorial.");
  }

  return res.json();
}

export async function deleteDocument(filename: string) {
  const res = await fetch(`${API_URL}/documents/${encodeURIComponent(filename)}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "No se pudo eliminar el documento.");
  }

  return res.json();
}

export async function resetMemory() {
  const res = await fetch(`${API_URL}/memory/reset`, { method: "POST" });
  if (!res.ok) throw new Error("No se pudo resetear la memoria.");
  return res.json();
}

export async function chatStream(
  message: string,
  sessionId?: string | null,
  onChunk?: (chunk: string) => void,
  signal?: AbortSignal
): Promise<{
  sessionId: string;
  finalText: string;
  detectedIntent: string | null;
  modeUsed: string | null;
  outputFormatUsed: string | null;
  sources: string[];
  attachments: string[];
}> {
  const res = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
    signal,
  });

  if (!res.ok || !res.body) {
    throw new Error("No se pudo iniciar el streaming.");
  }

  const returnedSessionId = res.headers.get("X-Session-Id") || "";
  const detectedIntent = res.headers.get("X-Detected-Intent");
  const modeUsed = res.headers.get("X-Mode-Used");
  const outputFormatUsed = res.headers.get("X-Output-Format");

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let finalText = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    finalText += chunk;
    onChunk?.(chunk);
  }

  return {
    sessionId: returnedSessionId,
    finalText,
    detectedIntent,
    modeUsed,
    outputFormatUsed,
    sources: [],
    attachments: [],
  };
}

export async function chatWithAttachments(
  message: string,
  files: File[],
  sessionId?: string | null,
  onChunk?: (chunk: string) => void,
  signal?: AbortSignal
): Promise<{
  sessionId: string;
  finalText: string;
  detectedIntent: string | null;
  modeUsed: string | null;
  outputFormatUsed: string | null;
  attachments: string[];
}> {
  const formData = new FormData();
  formData.append("message", message);
  if (sessionId) formData.append("session_id", sessionId);

  files.forEach((file) => formData.append("files", file));

  const res = await fetch(`${API_URL}/chat/attachments`, {
    method: "POST",
    body: formData,
    signal,
  });

  if (!res.ok || !res.body) {
    throw new Error("No se pudo iniciar el análisis con adjuntos.");
  }

  const returnedSessionId = res.headers.get("X-Session-Id") || "";
  const detectedIntent = res.headers.get("X-Detected-Intent");
  const modeUsed = res.headers.get("X-Mode-Used");
  const outputFormatUsed = res.headers.get("X-Output-Format");

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let finalText = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    finalText += chunk;
    onChunk?.(chunk);
  }

  return {
    sessionId: returnedSessionId,
    finalText,
    detectedIntent,
    modeUsed,
    outputFormatUsed,
    attachments: files.map((file) => file.name),
  };
}