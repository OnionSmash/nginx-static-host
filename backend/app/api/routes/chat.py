from fastapi import APIRouter, HTTPException

from app.core.rag import query_rag
from app.models.schemas import ChatRequest, ChatResponse, SourceDocument

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["rag"])
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Ask a question against the ingested document collection.

    The backend performs a similarity search over the vector store,
    retrieves the top-k chunks, and feeds them to the LLM to generate
    a grounded answer.
    """
    try:
        result = query_rag(request.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ChatResponse(
        answer=result["answer"],
        sources=[SourceDocument(**s) for s in result["sources"]],
    )
