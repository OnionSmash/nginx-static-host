from pydantic import BaseModel, Field


# ── Chat / RAG ─────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, examples=["What is Stacklume?"])


class SourceDocument(BaseModel):
    source: str
    page: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceDocument] = []


# ── Ingestion ──────────────────────────────────────────────────────────────────

class IngestTextRequest(BaseModel):
    content: str = Field(..., min_length=1)
    source_name: str = Field(default="manual", max_length=255)


class IngestUrlRequest(BaseModel):
    url: str = Field(..., examples=["https://docs.stacklume.com/intro"])


class IngestResponse(BaseModel):
    chunks_stored: int
    message: str
