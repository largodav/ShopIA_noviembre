from typing import Any

from app.core.config import settings
from app.services.ollama_client import ollama_client

INTENT_SYSTEM_PROMPT = """Eres el agente de intención de ShopIA (electrónica de El Corte Inglés).
Analiza la consulta breve del usuario y responde ÚNICAMENTE con un JSON válido con esta estructura exacta:
{
  "intent": "search" | "compare" | "recommend" | "price_check",
  "category": "TV y Vídeo" | "Informática" | "Telefonía" | "Sonido" | "Fotografía" | "Gaming" | "Electrónica",
  "keywords": ["palabra1", "palabra2"],
  "max_price_eur": null
}
Sé conciso y preciso en español."""


class IntentAgent:
    """Agente encargado de interpretar la intención de búsqueda predictiva usando Ollama."""

    async def analyze(self, query: str) -> tuple[dict[str, Any], bool]:
        result = await ollama_client.chat_json(
            model=settings.ollama_fast_model,
            system_prompt=INTENT_SYSTEM_PROMPT,
            user_prompt=f"Consulta del usuario: {query}",
            temperature=0.1,
        )
        if result:
            return {
                "raw_query": query,
                "intent": str(result.get("intent") or "search"),
                "category": str(result.get("category") or "Electrónica"),
                "keywords": result.get("keywords") if isinstance(result.get("keywords"), list) else [query],
                "max_price_eur": result.get("max_price_eur"),
            }, True

        return {
            "raw_query": query,
            "intent": "search",
            "category": "Electrónica",
            "keywords": [w for w in query.split() if len(w) > 1] or [query],
            "max_price_eur": None,
        }, False
