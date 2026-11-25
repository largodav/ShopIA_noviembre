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
    cards: list[InfoCard]


class PushSubscriptionPayload(BaseModel):
    endpoint: str
    keys: dict[str, str]
