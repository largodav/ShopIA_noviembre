from app.agents.advisor_agent import AdvisorAgent
from app.agents.eci_agent import EciAgent
from app.agents.intent_agent import IntentAgent
from app.models.schemas import InfoCard


class AgentOrchestrator:
    """Coordinador principal del sistema multi-agente con Ollama."""

    def __init__(self) -> None:
        self.intent_agent = IntentAgent()
        self.eci_agent = EciAgent()
        self.advisor_agent = AdvisorAgent()

    async def handle_predictive_query(self, query: str) -> list[InfoCard]:
        intent = await self.intent_agent.analyze(query)
        products = await self.eci_agent.search_electronics(query, intent)
        return await self.advisor_agent.build_cards(query, intent, products)


orchestrator = AgentOrchestrator()
