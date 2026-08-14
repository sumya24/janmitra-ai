"""FastAPI application entry point for JanSarthi AI."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import init_db
from backend.routes import admin, ask_janmitra, auth, complaints, locations, notifications

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize the database, then warm the RAG embedding model, on application startup.

    Warming the embedding model here (rather than leaving it fully lazy) matters in practice --
    measured directly while validating this: the FIRST live Ask Sarthi request after a fresh
    backend start paid the model's ~20-25s load cost inline, on top of normal retrieval+LLM
    latency, and exceeded a 30s client timeout in one such run. Warming it once at startup (a
    few extra seconds before the app reports ready, paid once, off the request path) avoids
    that. Best-effort: if this fails (e.g. no network on first run before the model is cached
    locally), the app still starts -- ask_janmitra_service.py's embedding provider is lazy by
    design and will retry the load on the first real request, matching the pre-warm-up behavior.
    """
    init_db()
    try:
        from backend.routes.ask_janmitra import _service

        _service._embedding_provider.load()
        logger.info("RAG embedding model warmed up at startup")
    except Exception as exc:
        logger.warning("Could not warm up the RAG embedding model at startup (will lazy-load on first request): %s", exc)
    logger.info("JanSarthi AI backend started")
    yield


app = FastAPI(title="JanSarthi AI", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Content-Disposition isn't in the browser's CORS-safelisted response headers, so without
    # explicitly exposing it, fetch()'s response.headers.get("Content-Disposition") silently
    # returns null on a cross-origin request (frontend :5173 -> backend :8000 in dev) even though
    # the header IS actually present -- curl/Postman never show this bug since CORS is a
    # browser-only restriction. That's what made the report download filename fall back to the
    # generic "report.pdf" (see frontend-react/src/lib/api.ts's requestBlob()) instead of the
    # real "JanSarthi_Complaint_JM-00042_Report.pdf" the backend was already sending correctly.
    expose_headers=["Content-Disposition"],
)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(complaints.router)
app.include_router(locations.router)
app.include_router(notifications.router)
app.include_router(ask_janmitra.router)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_FOLDER), name="uploads")


@app.get("/health")
def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}
