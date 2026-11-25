import json
import logging
import re
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def _extract_json_object(raw_text: str) -> dict[str, Any] | None:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return None
        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None


class OllamaClient:
    """Cliente asíncrono hacia Ollama local (Mac Apple Silicon o Windows NVIDIA)."""

    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")

    async def check_status(self) -> tuple[bool, list[str]]:
        try:
            async with httpx.AsyncClient(timeout=2.5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                return True, models
        except Exception:
            return False, []

    async def chat_json(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> dict[str, Any] | None:
        payload = {
            "model": model,
            "stream": False,
            "format": "json",
            "options": {"temperature": temperature},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        try:
            async with httpx.AsyncClient(timeout=settings.ollama_timeout_seconds) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data.get("message", {}).get("content", "")
                return _extract_json_object(content)
        except Exception as exc:
            logger.warning("Ollama chat_json falló (%s): %s", model, exc)
            return None

    async def embed(self, text: str) -> list[float] | None:
        payload = {
            "model": settings.ollama_embed_model,
            "prompt": text,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(f"{self.base_url}/api/embeddings", json=payload)
                resp.raise_for_status()
                embedding = resp.json().get("embedding")
                return embedding if isinstance(embedding, list) else None
        except Exception as exc:
            logger.warning("Ollama embed falló (%s): %s", settings.ollama_embed_model, exc)
            return None


ollama_client = OllamaClient()
