from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ollama_client import ollama_client

router = APIRouter()


class SelectModelRequest(BaseModel):
    model: str


@router.get("/")
async def list_local_models() -> dict:
    """Detecta los modelos LLM instalados en Ollama local."""
    reachable, models = await ollama_client.list_models_detailed()
    return {
        "reachable": reachable,
        "selected_model": ollama_client.selected_model,
        "models": models,
    }


@router.post("/select")
async def select_local_model(payload: SelectModelRequest) -> dict:
    """Cambia dinámicamente el modelo LLM activo en el backend."""
    reachable, models = await ollama_client.list_models_detailed()
    names = [m["name"] for m in models]
    if reachable and names and payload.model not in names:
        raise HTTPException(
            status_code=404,
            detail=f"El modelo '{payload.model}' no está instalado en Ollama local.",
        )
    selected = ollama_client.set_selected_model(payload.model)
    return {"status": "selected", "selected_model": selected}
