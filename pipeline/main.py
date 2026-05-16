from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

app = FastAPI(title="DocForge Pipeline", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "docforge-pipeline",
        "version": "0.1.0",
    }


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "DocForge pipeline is running. Use /health to check service status.",
    }
