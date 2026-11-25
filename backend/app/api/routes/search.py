from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.agents.orchestrator import orchestrator
from app.core.config import settings
from app.core.database import get_db
from app.models.schemas import PredictResponse

router = APIRouter()


@router.get("/predict", response_model=PredictResponse)
async def predict(
    q: str = Query(..., min_length=1, max_length=200),
    model: str | None = Query(default=None, max_length=120),
    db: Session = Depends(get_db),
) -> PredictResponse:
    cards, used_ollama, used_model = await orchestrator.handle_predictive_query(
        q, db, model_override=model
    )
    return PredictResponse(
        query=q,
        version=settings.app_version,
        ollamaActive=used_ollama,
        model=used_model if used_ollama else None,
        cards=cards,
    )
