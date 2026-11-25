from typing import Any

from app.core.config import settings
from app.models.schemas import InfoCard
from app.services.ollama_client import ollama_client

ADVISOR_SYSTEM_PROMPT = """Eres el agente asesor de ShopIA especializado en productos de electrónica de El Corte Inglés.
Cuando el usuario escribe una búsqueda predictiva, devuelve ÚNICAMENTE un JSON válido con 2 o 3 tarjetas útiles y breves en español:
{
  "cards": [
    {
      "type": "suggestion" | "comparison" | "product",
      "title": "Título corto y claro",
      "subtitle": "Subtítulo breve (ej. Guía rápida · TV y Vídeo)",
      "summary": "Explicación concisa en 1-2 frases con datos técnicos útiles.",
      "price": "Rango orientativo opcional o null",
      "tags": ["etiqueta1", "etiqueta2"]
    }
  ]
}
No inventes URLs ni precios exactos en stock si no están en el catálogo; usa rangos orientativos si ayuda."""


class AdvisorAgent:
    """Agente encargado de sintetizar tarjetas predictivas con Ollama."""

    async def build_cards(
        self, query: str, intent: dict[str, Any], products: list[dict[str, Any]]
    ) -> tuple[list[InfoCard], bool]:
        cards: list[InfoCard] = [
            InfoCard(
                id=item["id"],
                type="product",
                title=item["title"],
                subtitle=item.get("subtitle"),
                summary=item["summary"],
                price=item.get("price"),
                category=item.get("category"),
                sourceUrl=item.get("sourceUrl"),
                tags=item.get("tags", []),
            )
            for item in products
        ]

        user_prompt = (
            f"Consulta: {query}\n"
            f"Intención detectada: {intent.get('intent')}\n"
            f"Categoría: {intent.get('category')}\n"
            f"Productos ya encontrados en BD local: {len(products)}"
        )

        llm_response = await ollama_client.chat_json(
            model=settings.ollama_advisor_model,
            system_prompt=ADVISOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
        )

        if llm_response and isinstance(llm_response.get("cards"), list):
            for idx, raw_card in enumerate(llm_response["cards"][:3]):
                if not isinstance(raw_card, dict) or not raw_card.get("title"):
                    continue
                card_type = raw_card.get("type")
                if card_type not in ("product", "comparison", "suggestion", "status"):
                    card_type = "suggestion"
                cards.append(
                    InfoCard(
                        id=f"ollama-card-{idx + 1}",
                        type=card_type,
                        title=str(raw_card["title"])[:120],
                        subtitle=str(raw_card.get("subtitle") or f"Agente ShopIA · {intent.get('category')}"),
                        summary=str(raw_card.get("summary") or "")[:320],
                        price=str(raw_card["price"]) if raw_card.get("price") else None,
                        category=str(intent.get("category") or "Electrónica"),
                        tags=[str(t)[:24] for t in (raw_card.get("tags") or [])[:4]],
                    )
                )
            return cards, True

        cards.append(
            InfoCard(
                id="ollama-offline-fallback",
                type="status",
                title=f"Búsqueda registrada: «{query}»",
                subtitle=f"Backend {settings.app_version} · Ollama no disponible",
                summary=(
                    f"No se pudo conectar con Ollama en {settings.ollama_base_url} "
                    f"(modelo {settings.ollama_advisor_model}). Inicia Ollama en tu equipo para activar las respuestas IA."
                ),
                category=str(intent.get("category") or "Electrónica"),
                tags=["PostgreSQL OK", "Ollama Offline"],
            )
        )
        return cards, False
