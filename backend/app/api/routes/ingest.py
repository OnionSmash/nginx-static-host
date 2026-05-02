from fastapi import APIRouter, HTTPException, UploadFile, File

from app.core.ingestion import ingest_pdf_bytes, ingest_text, ingest_url
from app.models.schemas import IngestResponse, IngestTextRequest, IngestUrlRequest

router = APIRouter()


@router.post("/ingest/text", response_model=IngestResponse, tags=["ingestion"])
async def ingest_text_endpoint(request: IngestTextRequest) -> IngestResponse:
    """Ingest a plain-text document into the vector store."""
    try:
        n = ingest_text(request.content, source_name=request.source_name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return IngestResponse(chunks_stored=n, message=f"Stored {n} chunk(s) from '{request.source_name}'.")


@router.post("/ingest/pdf", response_model=IngestResponse, tags=["ingestion"])
async def ingest_pdf_endpoint(file: UploadFile = File(...)) -> IngestResponse:
    """Upload a PDF file and ingest its content into the vector store."""
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    try:
        data = await file.read()
        n = ingest_pdf_bytes(data, filename=file.filename or "upload.pdf")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return IngestResponse(chunks_stored=n, message=f"Stored {n} chunk(s) from '{file.filename}'.")


@router.post("/ingest/url", response_model=IngestResponse, tags=["ingestion"])
async def ingest_url_endpoint(request: IngestUrlRequest) -> IngestResponse:
    """Fetch a URL and ingest its text content into the vector store."""
    try:
        n = ingest_url(request.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return IngestResponse(chunks_stored=n, message=f"Stored {n} chunk(s) from '{request.url}'.")
