from typing import Literal
from pydantic import BaseModel, Field


CardType = Literal["product", "comparison", "suggestion", "status"]


class InfoCard(BaseModel):
    id: str
    type: CardType
    title: str
    subtitle: str | None = None
    summary: str
    price: str | None = None
    category: str | None = None
    sourceUrl: str | None = None
    tags: list[str] = Field(default_factory=list)


class PredictResponse(BaseModel):
    query: str
    version: str
    ollamaActive: bool = False
    model: str | None = None
    cards: list[InfoCard]


class PushSubscriptionPayload(BaseModel):
    endpoint: str
    keys: dict[str, str]
    userAgent: str | None = None


class PushUnsubscribePayload(BaseModel):
    endpoint: str


class PushTestRequest(BaseModel):
    title: str = "ShopIA"
    body: str = "Notificación Push enviada desde tu backend local (v001-b)."
    url: str = "./"
