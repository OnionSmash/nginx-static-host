from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # OpenAI
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # ChromaDB
    chroma_host: str = "chroma"
    chroma_port: int = 8000
    chroma_collection: str = "stacklume_docs"

    # RAG tuning
    retrieval_k: int = 5
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # App
    app_title: str = "Stacklume AI Backend"
    app_version: str = "1.0.0"
    cors_origins: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
