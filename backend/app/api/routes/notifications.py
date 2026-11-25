from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.schemas import (
    PushSubscriptionPayload,
    PushTestRequest,
    PushUnsubscribePayload,
)
from app.services.push_service import push_service

router = APIRouter()


@router.get("/vapid-public-key")
async def get_vapid_public_key() -> dict:
    return {
        "publicKey": settings.vapid_public_key,
        "configured": bool(settings.vapid_public_key and settings.vapid_private_key),
    }


@router.post("/subscribe")
async def subscribe_push(
    payload: PushSubscriptionPayload, db: Session = Depends(get_db)
) -> dict:
    sub = push_service.register_subscription(db, payload)
    return {"status": "subscribed", "id": sub.id}


@router.post("/unsubscribe")
async def unsubscribe_push(
    payload: PushUnsubscribePayload, db: Session = Depends(get_db)
) -> dict:
    removed = push_service.unregister_subscription(db, payload.endpoint)
    return {"status": "unsubscribed" if removed else "not_found"}


@router.post("/test")
async def send_test_push(
    payload: PushTestRequest = PushTestRequest(), db: Session = Depends(get_db)
) -> dict:
    return push_service.send_broadcast(
        db=db,
        title=payload.title,
        body=payload.body,
        url=payload.url,
    )
