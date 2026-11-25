from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.eci_agent import _upsert_products
from app.core.database import get_db
from app.models.db_models import Product
from app.services.eci_client import eci_client

router = APIRouter()


class ProductImportItem(BaseModel):
    sku: str | None = None
    title: str
    brand: str | None = None
    category: str | None = "Electrónica"
    price_eur: float | None = None
    summary: str | None = None
    source_url: str | None = None
    image_url: str | None = None


@router.get("/")
async def list_products(limit: int = 20, db: Session = Depends(get_db)) -> dict:
    """Devuelve productos de electrónica almacenados en PostgreSQL."""
    rows = db.scalars(select(Product).order_by(Product.updated_at.desc()).limit(limit)).all()
    return {
        "count": len(rows),
        "items": [
            {
                "id": p.id,
                "sku": p.sku,
                "title": p.title,
                "brand": p.brand,
                "category": p.category,
                "price_eur": p.price_eur,
                "summary": p.summary,
                "source_url": p.source_url,
            }
            for p in rows
        ],
    }


@router.post("/sync")
async def sync_from_eci(
    q: str = Query(..., min_length=2, max_length=120),
    db: Session = Depends(get_db),
) -> dict:
    """Consulta el catálogo público de electrónica de El Corte Inglés y guarda resultados en BD."""
    live = await eci_client.search_live(q, limit=8)
    saved = _upsert_products(db, live["items"], default_category="Electrónica") if live["items"] else []
    return {
        "query": q,
        "status": live["status"],
        "http_status": live["http_status"],
        "search_url": live["search_url"],
        "saved_count": len(saved),
    }


@router.post("/import")
async def import_products(
    items: list[ProductImportItem],
    db: Session = Depends(get_db),
) -> dict:
    """Permite importar manualmente productos de electrónica al catálogo local en PostgreSQL."""
    saved = _upsert_products(
        db, [item.model_dump() for item in items], default_category="Electrónica"
    )
    return {"saved_count": len(saved)}
