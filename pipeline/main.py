from pathlib import Path
import tempfile
import shutil
import logging
import time

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from .orchestrator import IngestionOrchestrator
from .extractors.base import ExtractionError

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

app = FastAPI(title="DocForge Pipeline", version="0.1.0")
LOGGER = logging.getLogger(__name__)

# Upload limits
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB

orchestrator = IngestionOrchestrator()


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


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    """Accept a PDF upload, run the ingestion orchestrator, and return an ExtractionResult."""
    # Basic validation
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported")

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        temp_path = Path(tmp.name)
        total = 0
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_UPLOAD_SIZE:
                tmp.close()
                temp_path.unlink(missing_ok=True)
                raise HTTPException(status_code=400, detail="File too large")
            tmp.write(chunk)

    try:
        start = time.perf_counter()
        result = orchestrator.ingest(temp_path)
        elapsed = (time.perf_counter() - start) * 1000.0
        data = result.model_dump() if hasattr(result, 'model_dump') else result.dict()
        data['total_extraction_time_ms'] = elapsed
        return JSONResponse(content=data)
    except ExtractionError as e:
        LOGGER.error("Extraction failed: %s", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except Exception:
            pass
