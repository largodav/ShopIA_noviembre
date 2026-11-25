from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.db_models import Product

router = APIRouter()


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
