from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import notifications, products, search
from app.core.config import settings

app = FastAPI(
    title="ShopIA Backend",
    description="API y sistema multi-agente local con Ollama para productos de electrónica de El Corte Inglés.",
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "shopia-backend",
        "version": settings.app_version,
        "ollama_url": settings.ollama_base_url,
    }
