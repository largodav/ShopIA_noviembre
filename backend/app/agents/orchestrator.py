import time

from sqlalchemy.orm import Session

from app.agents.advisor_agent import AdvisorAgent
from app.agents.eci_agent import EciAgent
from app.agents.intent_agent import IntentAgent
from app.models.db_models import SearchHistory
from app.models.schemas import InfoCard
from app.services.ollama_client import ollama_client

CACHE_TTL_SECONDS = 60.0


class AgentOrchestrator:
    """Coordinador principal del sistema multi-agente con Ollama, catálogo ECI y PostgreSQL."""

    def __init__(self) -> None:
        self.intent_agent = IntentAgent()
        self.eci_agent = EciAgent()
        self.advisor_agent = AdvisorAgent()
        self._cache: dict[str, tuple[float, list[InfoCard], bool, str]] = {}

    async def handle_predictive_query(
        self, query: str, db: Session, model_override: str | None = None
    ) -> tuple[list[InfoCard], bool, str]:
        active_model = (model_override or ollama_client.selected_model).strip()
        cache_key = f"{active_model}::{query.strip().lower()}"
        now = time.monotonic()
        cached = self._cache.get(cache_key)
        if cached and (now - cached[0]) < CACHE_TTL_SECONDS:
            return cached[1], cached[2], cached[3]

        intent, intent_used_ollama = await self.intent_agent.analyze(query)
        products, eci_meta = await self.eci_agent.search_electronics(query, intent, db)
        cards, advisor_used_ollama, used_model = await self.advisor_agent.build_cards(
            query, intent, products, eci_meta, model_override=active_model
        )

        used_ollama = intent_used_ollama or advisor_used_ollama

        if used_ollama:
            self._cache[cache_key] = (now, cards, used_ollama, used_model)

        history_row = SearchHistory(
            query=query,
            detected_intent=str(intent.get("intent") or "search"),
            detected_category=str(intent.get("category") or "Electrónica"),
            used_ollama=used_ollama,
            results_count=len(cards),
        )
        db.add(history_row)
        db.commit()

        return cards, used_ollama, used_model


orchestrator = AgentOrchestrator()
