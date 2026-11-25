from fastapi import APIRouter, Query

from app.agents.orchestrator import orchestrator
from app.core.config import settings
from app.models.schemas import PredictResponse

router = APIRouter()


@router.get("/predict", response_model=PredictResponse)
async def predict(q: str = Query(..., min_length=1, max_length=200)) -> PredictResponse:
    cards = await orchestrator.handle_predictive_query(q)
    return PredictResponse(
        query=q,
        version=settings.app_version,
        cards=cards,
    )
