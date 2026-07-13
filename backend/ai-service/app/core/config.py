from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from amenbank_shared.config import BaseServiceSettings


class Settings(BaseServiceSettings):
    service_name: str = "ai-service"
    chroma_host: str = "localhost"
    chroma_port: int = 8100
    chroma_collection: str = "amen_bank_kb"
    chroma_persist_dir: str = str(Path(__file__).resolve().parents[2] / "vector_database" / "chroma")
    embedding_model: str = "paraphrase-multilingual-mpnet-base-v2"
    llm_provider: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    top_k: int = 5
    chunks_path: str = str(Path(__file__).resolve().parents[2] / "datasets" / "processed" / "chunks.json")


settings = Settings()
