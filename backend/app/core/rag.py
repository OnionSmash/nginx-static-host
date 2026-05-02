from __future__ import annotations

from functools import lru_cache

import chromadb
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

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


def build_rag_chain() -> RetrievalQA:
    cfg = get_settings()
    llm = ChatOpenAI(
        model=cfg.openai_chat_model,
        openai_api_key=cfg.openai_api_key,
        temperature=0,
    )
    retriever = get_vector_store().as_retriever(
        search_type="similarity",
        search_kwargs={"k": cfg.retrieval_k},
    )
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": _SYSTEM_PROMPT},
    )


def query_rag(question: str) -> dict:
    """Run a RAG query and return answer + source metadata."""
    chain = build_rag_chain()
    result = chain.invoke({"query": question})
    sources = [
        {
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page"),
        }
        for doc in result.get("source_documents", [])
    ]
    return {"answer": result["result"], "sources": sources}
