from __future__ import annotations

import ipaddress
import socket
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from app.core.config import get_settings
from app.core.rag import get_vector_store


def _splitter() -> RecursiveCharacterTextSplitter:
    cfg = get_settings()
    return RecursiveCharacterTextSplitter(
        chunk_size=cfg.chunk_size,
        chunk_overlap=cfg.chunk_overlap,
    )


def _validate_url(url: str) -> None:
    """Raise ValueError if the URL targets a private/loopback address (SSRF guard)."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http and https URLs are allowed.")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Invalid URL: missing hostname.")

    try:
        resolved_ip = socket.getaddrinfo(hostname, None)[0][4][0]
        addr = ipaddress.ip_address(resolved_ip)
    except (socket.gaierror, ValueError) as exc:
        raise ValueError(f"Could not resolve hostname '{hostname}'.") from exc

    if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
        raise ValueError("Requests to private/internal addresses are not allowed.")


def ingest_text(content: str, source_name: str = "manual") -> int:
    """Ingest a plain-text string. Returns number of chunks stored."""
    from langchain.schema import Document

    splitter = _splitter()
    docs = splitter.create_documents([content], metadatas=[{"source": source_name}])
    store = get_vector_store()
    store.add_documents(docs)
    return len(docs)


def ingest_pdf_bytes(data: bytes, filename: str) -> int:
    """Ingest a PDF from raw bytes. Returns number of chunks stored."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        for page in pages:
            page.metadata["source"] = filename

        splitter = _splitter()
        chunks = splitter.split_documents(pages)
        store = get_vector_store()
        store.add_documents(chunks)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return len(chunks)


def ingest_url(url: str) -> int:
    """Fetch a URL, strip HTML, ingest as text. Returns number of chunks stored."""
    _validate_url(url)

    resp = requests.get(url, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    # Remove script / style noise
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)

    return ingest_text(text, source_name=url)
