from app.models.schemas import InfoCard


class AdvisorAgent:
    """Agente encargado de sintetizar resultados en tarjetas predictivas para el usuario."""

    async def build_cards(
        self, query: str, intent: dict[str, str], products: list[dict]
    ) -> list[InfoCard]:
        cards = [
            InfoCard(
                id=item["id"],
                type="product",
                title=item["title"],
                subtitle="El Corte Inglés · Electrónica",
                summary=item["summary"],
                price=item.get("price"),
                category=item.get("category"),
                tags=item.get("tags", []),
            )
            for item in products
        ]
        cards.append(
            InfoCard(
                id="agent-status-v001a",
                type="status",
                title=f"Consulta recibida: «{query}»",
                subtitle="Orquestador ShopIA · v001-a",
                summary="Conexión con backend local operativa. Listo para conectar Ollama y catálogo ECI en la siguiente versión.",
                tags=["FastAPI", "Ollama Ready"],
            )
        )
        return cards
