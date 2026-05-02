from __future__ import annotations

from functools import lru_cache

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.config import get_settings

_SYSTEM_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are a helpful AI assistant for the Stacklume platform.\n"
        "Use ONLY the context below to answer the question. "
        "If you cannot find the answer in the context, say so clearly.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    ),
)


@lru_cache
def _chroma_client() -> chromadb.HttpClient:
    cfg = get_settings()
    return chromadb.HttpClient(host=cfg.chroma_host, port=cfg.chroma_port)


def get_vector_store() -> Chroma:
    cfg = get_settings()
    embeddings = OpenAIEmbeddings(
        model=cfg.openai_embedding_model,
        openai_api_key=cfg.openai_api_key,
    )
    return Chroma(
        client=_chroma_client(),
        collection_name=cfg.chroma_collection,
        embedding_function=embeddings,
    )


def query_rag(question: str) -> dict:
    """Run a RAG query and return answer + source metadata."""
    cfg = get_settings()

    retriever = get_vector_store().as_retriever(
        search_type="similarity",
        search_kwargs={"k": cfg.retrieval_k},
    )
    docs: list[Document] = retriever.invoke(question)

    context = "\n\n".join(doc.page_content for doc in docs)
    prompt_text = _SYSTEM_PROMPT.format(context=context, question=question)

    llm = ChatOpenAI(
        model=cfg.openai_chat_model,
        openai_api_key=cfg.openai_api_key,
        temperature=0,
    )
    response = llm.invoke(prompt_text)

    sources = [
        {
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page"),
        }
        for doc in docs
    ]
    return {"answer": response.content, "sources": sources}
