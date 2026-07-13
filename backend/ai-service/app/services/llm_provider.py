import json
from abc import ABC, abstractmethod
from pathlib import Path

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, language: str) -> str:
        pass


class MockLLMProvider(LLMProvider):
    async def generate(self, prompt: str, language: str) -> str:
        context_start = prompt.find("Context:")
        context = prompt[context_start:context_start + 500] if context_start >= 0 else ""
        lang_labels = {"fr": "français", "ar": "العربية", "en": "English"}
        return (
            f"Basé sur la documentation Amen Bank ({lang_labels.get(language, language)}), "
            f"voici une réponse fondée sur nos sources internes. "
            f"{context[:200].strip()}..."
            if language == "fr"
            else f"Based on Amen Bank documentation: {context[:200].strip()}..."
        )


class OpenAIProvider(LLMProvider):
    async def generate(self, prompt: str, language: str) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": f"Answer in {language}. Use only provided context."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]


class OllamaProvider(LLMProvider):
    async def generate(self, prompt: str, language: str) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json()["response"]


def get_llm_provider() -> LLMProvider:
    providers = {"mock": MockLLMProvider, "openai": OpenAIProvider, "ollama": OllamaProvider}
    cls = providers.get(settings.llm_provider, MockLLMProvider)
    return cls()
