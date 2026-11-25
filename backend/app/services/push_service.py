import json
import logging

from pywebpush import WebPushException, webpush
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.db_models import PushSubscription
from app.models.schemas import PushSubscriptionPayload

logger = logging.getLogger(__name__)


class PushService:
    """Gestión persistente en PostgreSQL y envío real de notificaciones Web Push (VAPID)."""

    def register_subscription(
        self, db: Session, payload: PushSubscriptionPayload
    ) -> PushSubscription:
        existing = db.scalar(
            select(PushSubscription).where(PushSubscription.endpoint == payload.endpoint)
        )
        p256dh = payload.keys.get("p256dh", "")
        auth = payload.keys.get("auth", "")

        if existing:
            existing.p256dh = p256dh
            existing.auth = auth
            existing.user_agent = payload.userAgent
            existing.active = True
            db.commit()
            db.refresh(existing)
            return existing

        sub = PushSubscription(
            endpoint=payload.endpoint,
            p256dh=p256dh,
            auth=auth,
            user_agent=payload.userAgent,
            active=True,
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return sub

    def unregister_subscription(self, db: Session, endpoint: str) -> bool:
        existing = db.scalar(
            select(PushSubscription).where(PushSubscription.endpoint == endpoint)
        )
        if not existing:
            return False
        existing.active = False
        db.commit()
        return True

    def send_broadcast(self, db: Session, title: str, body: str, url: str = "./") -> dict:
        if not (settings.vapid_public_key and settings.vapid_private_key):
            return {
                "configured": False,
                "sent": 0,
                "failed": 0,
                "total": 0,
                "detail": "Claves VAPID no configuradas en infra/.env",
            }

        subs = db.scalars(
            select(PushSubscription).where(PushSubscription.active.is_(True))
        ).all()

        payload = json.dumps({"title": title, "body": body, "url": url})
        sent = 0
        failed = 0

        for sub in subs:
            subscription_info = {
                "endpoint": sub.endpoint,
                "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
            }
            try:
                webpush(
                    subscription_info=subscription_info,
                    data=payload,
                    vapid_private_key=settings.vapid_private_key,
                    vapid_claims={"sub": settings.vapid_subject},
                )
                sent += 1
            except WebPushException as exc:
                failed += 1
                status_code = getattr(exc.response, "status_code", None)
                logger.warning("Error enviando Web Push (%s): %s", status_code, exc)
                if status_code in (404, 410):
                    sub.active = False

        db.commit()
        return {
            "configured": True,
            "sent": sent,
            "failed": failed,
            "total": len(subs),
        }


push_service = PushService()
