from app.models.schemas import PushSubscriptionPayload


class PushService:
    """Gestión de suscripciones y envío de notificaciones Web Push (base v001-a)."""

    def __init__(self) -> None:
        self._subscriptions: list[PushSubscriptionPayload] = []

    def register_subscription(self, payload: PushSubscriptionPayload) -> None:
        if all(sub.endpoint != payload.endpoint for sub in self._subscriptions):
            self._subscriptions.append(payload)


push_service = PushService()
