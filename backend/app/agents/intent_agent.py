class IntentAgent:
    """Agente encargado de interpretar la intención de búsqueda predictiva."""

    async def analyze(self, query: str) -> dict[str, str]:
        return {
            "raw_query": query,
            "intent": "electronics_search",
        }
