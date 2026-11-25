from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.db_models import Product


class EciAgent:
    """Agente encargado de buscar productos de electrónica en PostgreSQL (catálogo ECI cacheado)."""

    async def search_electronics(
        self, query: str, intent: dict[str, Any], db: Session
    ) -> list[dict[str, Any]]:
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
        rows = db.scalars(stmt).all()
        return [
            {
                "id": f"db-prod-{p.id}",
                "title": p.title,
                "subtitle": f"El Corte Inglés · {p.category or 'Electrónica'}",
                "summary": p.summary or "Producto almacenado en el catálogo local de ShopIA.",
                "price": f"{p.price_eur:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
                if p.price_eur is not None
                else None,
                "category": p.category or "Electrónica",
                "sourceUrl": p.source_url,
                "tags": [t for t in [p.brand, p.category] if t],
            }
            for p in rows
        ]
