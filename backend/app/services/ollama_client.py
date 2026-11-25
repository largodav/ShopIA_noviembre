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
    """Cliente asíncrono hacia Ollama local con descubrimiento y selección dinámica de modelos."""

    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.selected_model: str = settings.ollama_advisor_model

    def set_selected_model(self, model_name: str) -> str:
        self.selected_model = model_name.strip()
        return self.selected_model

    async def list_models_detailed(self) -> tuple[bool, list[dict[str, Any]]]:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()
                data = resp.json()
                models = []
                for m in data.get("models", []):
                    name = m.get("name")
                    if not name:
                        continue
                    size_bytes = m.get("size") or 0
                    details = m.get("details") or {}
                    models.append(
                        {
                            "name": name,
                            "size_gb": round(size_bytes / (1024**3), 2) if size_bytes else None,
                            "family": details.get("family"),
                            "parameter_size": details.get("parameter_size"),
                            "quantization": details.get("quantization_level"),
                        }
                    )
                return True, models
        except Exception:
            return False, []

    async def check_status(self) -> tuple[bool, list[str]]:
        ok, detailed = await self.list_models_detailed()
        return ok, [m["name"] for m in detailed]

    async def chat_json(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        num_predict: int = 900,
    ) -> dict[str, Any] | None:
        payload = {
            "model": model,
            "stream": False,
            "format": "json",
            "think": False,
            "keep_alive": "10m",
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,
            },
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
                parsed = _extract_json_object(content)
                if parsed is None:
                    logger.warning("Ollama devolvió JSON inválido (%s): %s", model, content[:240])
                return parsed
        except Exception as exc:
            logger.warning("Ollama chat_json falló (%s): %s: %s", model, type(exc).__name__, exc)
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
            logger.warning(
                "Ollama embed falló (%s): %s: %s",
                settings.ollama_embed_model,
                type(exc).__name__,
                exc,
            )
            return None


ollama_client = OllamaClient()
