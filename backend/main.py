"""FastAPI application entry point for JanMitra AI."""

import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import init_db
from backend.routes import complaints

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="JanMitra AI", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    """Initialize the database on application startup."""
    init_db()
    logger.info("JanMitra AI backend started")


app.include_router(complaints.router)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_FOLDER), name="uploads")


@app.get("/health")
def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}
