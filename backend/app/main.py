from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import notifications, products, search
from app.core.config import settings
from app.core.database import init_db
from app.services.ollama_client import ollama_client


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="ShopIA Backend",
    description="API y sistema multi-agente local con Ollama para productos de electrónica de El Corte Inglés.",
    version=settings.app_version,
    lifespan=lifespan,
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
async def health_check() -> dict:
    ollama_ok, models = await ollama_client.check_status()
    return {
        "status": "ok",
        "service": "shopia-backend",
        "version": settings.app_version,
        "ollama": {
            "url": settings.ollama_base_url,
            "reachable": ollama_ok,
            "fast_model": settings.ollama_fast_model,
            "advisor_model": settings.ollama_advisor_model,
            "available_models_count": len(models),
        },
        "web_push_configured": bool(settings.vapid_public_key and settings.vapid_private_key),
    }
