"""FastAPI backend for the Alfred Lab chatbot web UI."""

import json
from functools import lru_cache
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

from src.chatbot import create_chatbot
from src.config import (
    COMPANY_NAME,
    CONTACT_EMAIL,
    CONTACT_HOURS,
    CONTACT_PHONE,
    FAISS_INDEX_PATH,
    SESSION_REQUESTS_PATH,
)


class ChatRequest(BaseModel):
    """Incoming chat request."""

    message: str = Field(..., min_length=1, max_length=2000)


class Source(BaseModel):
    """Source document returned by retrieval."""

    title: str
    url: str
    preview: str


class ChatResponse(BaseModel):
    """Outgoing chat response."""

    answer: str
    sources: list[Source]


class SessionRequest(BaseModel):
    """One-on-one session request from the web UI."""

    name: str = Field(..., min_length=2, max_length=120)
    email: str = Field(..., min_length=5, max_length=160)
    organization: str = Field(..., min_length=2, max_length=160)
    topic: str = Field(..., min_length=2, max_length=240)


app = FastAPI(title=f"{COMPANY_NAME} Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def get_chatbot():
    """Create one chatbot instance for the API process."""
    return create_chatbot()


@app.get("/api/health")
def health() -> dict[str, Any]:
    """Return backend and FAISS readiness."""
    return {
        "status": "ok",
        "company": COMPANY_NAME,
        "faiss_ready": FAISS_INDEX_PATH.exists(),
    }


@app.get("/api/contact")
def contact() -> dict[str, str]:
    """Return official contact details."""
    return {
        "phone": CONTACT_PHONE,
        "email": CONTACT_EMAIL,
        "hours": CONTACT_HOURS,
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Answer a user question using the local FAISS knowledge base."""
    try:
        result = get_chatbot().chat(request.message.strip())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    sources = []
    for source in result.get("sources", []):
        metadata = source.get("metadata", {})
        sources.append(
            Source(
                title=metadata.get("title") or "Alfred Lab",
                url=metadata.get("url") or "",
                preview=source.get("content") or "",
            )
        )

    return ChatResponse(answer=result["answer"], sources=sources)


@app.get("/api/history")
def history() -> dict[str, Any]:
    """Return in-memory conversation history."""
    return {"messages": get_chatbot().get_chat_history()}


@app.post("/api/clear")
def clear_history() -> dict[str, str]:
    """Clear in-memory conversation history."""
    get_chatbot().clear_history()
    return {"status": "cleared"}


@app.post("/api/session-request")
def session_request(request: SessionRequest) -> dict[str, str]:
    """Store a one-on-one session request locally."""
    SESSION_REQUESTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing_requests = []
    if SESSION_REQUESTS_PATH.exists():
        with SESSION_REQUESTS_PATH.open("r", encoding="utf-8") as file:
            existing_requests = json.load(file)

    existing_requests.append(
        {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "name": request.name,
            "email": request.email,
            "organization": request.organization,
            "topic": request.topic,
        }
    )

    with SESSION_REQUESTS_PATH.open("w", encoding="utf-8") as file:
        json.dump(existing_requests, file, indent=2)

    return {"status": "received", "message": "Your one-on-one session request has been saved."}
