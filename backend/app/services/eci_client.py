class EciClient:
    """Cliente de datos de electrónica de El Corte Inglés (stub inicial en v001-a)."""

    async def search_stub(self, query: str) -> list[dict]:
        return [
            {
                "id": "eci-stub-1",
                "title": f"Resultado de prueba para «{query}»",
                "summary": "Placeholder del conector de electrónica de El Corte Inglés para v001-a.",
                "price": "— €",
                "category": "Electrónica",
                "tags": ["ECI", "v001-a"],
            }
        ]


eci_client = EciClient()
