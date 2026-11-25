from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.db_models import Product
from app.services.eci_client import eci_client


def _format_price(price_eur: float | None) -> str | None:
    if price_eur is None:
        return None
    return f"{price_eur:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def _upsert_products(db: Session, raw_items: list[dict[str, Any]], default_category: str) -> list[Product]:
    saved: list[Product] = []
    for item in raw_items:
        title = (item.get("title") or "").strip()
        if not title:
            continue
        sku = item.get("sku")
        source_url = item.get("source_url")

        existing = None
        if sku:
            existing = db.scalar(select(Product).where(Product.sku == sku))
        if not existing and source_url:
            existing = db.scalar(select(Product).where(Product.source_url == source_url))

        if existing:
            existing.title = title
            existing.brand = item.get("brand") or existing.brand
            existing.category = item.get("category") or default_category
            if item.get("price_eur") is not None:
                existing.price_eur = item["price_eur"]
            existing.summary = item.get("summary") or existing.summary
            existing.image_url = item.get("image_url") or existing.image_url
            saved.append(existing)
        else:
            prod = Product(
                sku=sku,
                title=title,
                brand=item.get("brand"),
                category=item.get("category") or default_category,
                price_eur=item.get("price_eur"),
                summary=item.get("summary"),
                source_url=source_url,
                image_url=item.get("image_url"),
            )
            db.add(prod)
            saved.append(prod)

    if saved:
        db.commit()
        for p in saved:
            db.refresh(p)
    return saved


class EciAgent:
    """Agente encargado de buscar y cachear productos de electrónica de El Corte Inglés."""

    async def search_electronics(
        self, query: str, intent: dict[str, Any], db: Session, live_sync: bool = True
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        pattern = f"%{query.strip()}%"
        stmt = (
            select(Product)
            .where(
                or_(
                    Product.title.ilike(pattern),
                    Product.category.ilike(pattern),
                    Product.brand.ilike(pattern),
                    Product.summary.ilike(pattern),
                )
            )
            .order_by(Product.updated_at.desc())
            .limit(4)
        )
        rows = list(db.scalars(stmt).all())
        eci_meta: dict[str, Any] = {"source": "db_cache", "status": "ok" if rows else "empty"}

        if not rows and live_sync:
            live = await eci_client.search_live(query, limit=4)
            eci_meta = {
                "source": "eci_live",
                "status": live["status"],
                "search_url": live["search_url"],
            }
            if live["items"]:
                rows = _upsert_products(
                    db,
                    live["items"],
                    default_category=str(intent.get("category") or "Electrónica"),
                )

        items = [
            {
                "id": f"db-prod-{p.id}",
                "title": p.title,
                "subtitle": f"El Corte Inglés · {p.category or 'Electrónica'}",
                "summary": p.summary or "Producto de electrónica de El Corte Inglés.",
                "price": _format_price(p.price_eur),
                "category": p.category or "Electrónica",
                "sourceUrl": p.source_url,
                "tags": [t for t in [p.brand, p.category, "ECI"] if t],
            }
            for p in rows
        ]
        return items, eci_meta
