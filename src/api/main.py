from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from src.api.dependencies import build_messages_for_model, build_services
from src.api.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    MemoryResetResponse,
    RebuildResponse,
    SessionDetail,
    SessionMessage,
    SessionSummary,
    UploadResponse,
)
from src.app.document_service import DocumentService
from src.config.settings import OLLAMA_CHAT_MODEL
from src.llm.ollama_client import check_ollama_connection, clean_response
from src.memory.memory_extractor import extract_memory_fact
from src.memory.memory_service import append_message_to_memory, reset_persistent_memory
from src.routing.router import detect_intent

app = FastAPI(title="Chatbot Local API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    rag_status = DocumentService.get_rag_status()

    try:
        ollama_info = check_ollama_connection()
        models = [model["name"] for model in ollama_info.get("models", [])]

        return HealthResponse(
            ok=True,
            ollama_connected=True,
            model=OLLAMA_CHAT_MODEL,
            model_available=OLLAMA_CHAT_MODEL in models,
            document_count=rag_status["document_count"],
            indexed_chunks=rag_status["indexed_chunks"],
            vectorstore_exists=rag_status["vectorstore_exists"],
        )
    except Exception:
        return HealthResponse(
            ok=False,
            ollama_connected=False,
            model=OLLAMA_CHAT_MODEL,
            model_available=False,
            document_count=rag_status["document_count"],
            indexed_chunks=rag_status["indexed_chunks"],
            vectorstore_exists=rag_status["vectorstore_exists"],
        )


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    chat_service, session_service = build_services()

    session_id = chat_service.ensure_session(payload.session_id)
    messages_for_model = build_messages_for_model(
        session_service=session_service,
        session_id=session_id,
        current_prompt=payload.message,
    )

    response = chat_service.process_message(
        session_id=session_id,
        user_message=payload.message,
        messages_for_model=messages_for_model,
    )

    memory_fact = extract_memory_fact(payload.message)
    if memory_fact:
        append_message_to_memory("user", memory_fact)

    return ChatResponse(
        session_id=session_id,
        answer=clean_response(response.answer),
        detected_intent=response.detected_intent,
        tools_used=response.tools_used,
        sources=response.sources,
    )


@app.post("/chat/stream")
def chat_stream(payload: ChatRequest):
    chat_service, session_service = build_services()

    session_id = chat_service.ensure_session(payload.session_id)
    messages_for_model = build_messages_for_model(
        session_service=session_service,
        session_id=session_id,
        current_prompt=payload.message,
    )

    detected_intent = detect_intent(payload.message)

    def generate():
        accumulated = ""
        already_sent = ""

        for event in chat_service.stream_message(
            session_id=session_id,
            user_message=payload.message,
            messages_for_model=messages_for_model,
        ):
            chunk = event["content"]

            if event["type"] == "final":
                accumulated = chunk
            else:
                accumulated += chunk

            cleaned_full = clean_response(accumulated)

            if len(cleaned_full) > len(already_sent):
                delta = cleaned_full[len(already_sent):]
                already_sent = cleaned_full
                if delta:
                    yield delta

        memory_fact = extract_memory_fact(payload.message)
        if memory_fact:
            append_message_to_memory("user", memory_fact)

    headers = {
        "X-Session-Id": session_id,
        "X-Detected-Intent": detected_intent,
        "X-Model": OLLAMA_CHAT_MODEL,
    }
    return StreamingResponse(generate(), media_type="text/plain", headers=headers)


@app.get("/sessions", response_model=list[SessionSummary])
def list_sessions():
    _, session_service = build_services()
    sessions = session_service.list_sessions()

    return [
        SessionSummary(
            session_id=s.session_id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in sessions
    ]


@app.post("/sessions", response_model=SessionSummary)
def create_session():
    _, session_service = build_services()
    session = session_service.create_session()

    return SessionSummary(
        session_id=session.session_id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@app.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session(session_id: str):
    _, session_service = build_services()
    session = session_service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")

    return SessionDetail(
        session_id=session.session_id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[
            SessionMessage(
                role=m.role,
                content=m.content,
                timestamp=m.timestamp,
            )
            for m in session.messages
        ],
    )


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    _, session_service = build_services()
    session_service.delete_session(session_id)
    return {"ok": True}


@app.get("/documents")
def list_documents():
    return {
        "status": DocumentService.get_rag_status(),
        "documents": DocumentService.list_documents(),
    }


@app.post("/documents/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    content = await file.read()
    saved_path, indexed_chunks = DocumentService.save_file_bytes(file.filename, content)
    return UploadResponse(
        path=saved_path,
        filename=file.filename,
        indexed_chunks=indexed_chunks,
    )


@app.delete("/documents/{filename}")
def delete_document(filename: str):
    result = DocumentService.delete_document(filename)

    if not result["deleted_file"]:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")

    return {
        "ok": True,
        "deleted_chunks": result["deleted_chunks"],
    }


@app.post("/documents/rebuild", response_model=RebuildResponse)
def rebuild_documents():
    try:
        total_chunks = DocumentService.rebuild_vectorstore()
        return RebuildResponse(total_chunks=total_chunks)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/memory/reset", response_model=MemoryResetResponse)
def reset_memory():
    reset_persistent_memory()
    return MemoryResetResponse(ok=True)