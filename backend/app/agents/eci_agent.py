from app.services.eci_client import eci_client


class EciAgent:
    """Agente encargado de recuperar y normalizar productos de electrónica de El Corte Inglés."""

    async def search_electronics(self, query: str, intent: dict[str, str]) -> list[dict]:
        return await eci_client.search_stub(query)
