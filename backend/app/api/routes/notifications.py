from fastapi import APIRouter

from app.models.schemas import PushSubscriptionPayload
from app.services.push_service import push_service

router = APIRouter()


@router.post("/subscribe")
async def subscribe_push(payload: PushSubscriptionPayload) -> dict[str, str]:
    push_service.register_subscription(payload)
    return {"status": "subscribed"}
