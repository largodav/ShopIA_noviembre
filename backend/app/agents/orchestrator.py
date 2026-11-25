from sqlalchemy.orm import Session

from app.agents.advisor_agent import AdvisorAgent
from app.agents.eci_agent import EciAgent
from app.agents.intent_agent import IntentAgent
from app.models.db_models import SearchHistory
from app.models.schemas import InfoCard


class AgentOrchestrator:
    """Coordinador principal del sistema multi-agente con Ollama y PostgreSQL."""

    def __init__(self) -> None:
        self.intent_agent = IntentAgent()
        self.eci_agent = EciAgent()
        self.advisor_agent = AdvisorAgent()

    async def handle_predictive_query(self, query: str, db: Session) -> tuple[list[InfoCard], bool]:
        intent, intent_used_ollama = await self.intent_agent.analyze(query)
        products = await self.eci_agent.search_electronics(query, intent, db)
        cards, advisor_used_ollama = await self.advisor_agent.build_cards(query, intent, products)

        used_ollama = intent_used_ollama or advisor_used_ollama

        history_row = SearchHistory(
            query=query,
            detected_intent=str(intent.get("intent") or "search"),
            detected_category=str(intent.get("category") or "Electrónica"),
            used_ollama=used_ollama,
            results_count=len(cards),
        )
        db.add(history_row)
        db.commit()

        return cards, used_ollama


orchestrator = AgentOrchestrator()
