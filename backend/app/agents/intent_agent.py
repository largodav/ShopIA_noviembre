from typing import Any


CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("TV y Vídeo", ("tv", "tele", "oled", "qled", "miniled", "proyector", "barra de sonido")),
    ("Informática", ("portatil", "portátil", "macbook", "ordenador", "pc", "monitor", "tablet", "ipad", "ssd")),
    ("Telefonía", ("movil", "móvil", "iphone", "samsung", "galaxy", "pixel", "xiaomi", "smartphone")),
    ("Sonido", ("auricular", "cascos", "altavoz", "airpods", "sonos", "bose", "bluetooth")),
    ("Fotografía", ("camara", "cámara", "objetivo", "reflex", "réflex", "canon", "sony alpha", "nikon")),
    ("Gaming", ("ps5", "playstation", "xbox", "nintendo", "switch", "grafica", "gráfica", "rtx")),
]


class IntentAgent:
    """Agente de intención ultrarrápido (<1ms) para no duplicar llamadas a Ollama en búsqueda predictiva."""

    async def analyze(self, query: str) -> tuple[dict[str, Any], bool]:
        q = query.lower()

        intent = "search"
        if any(w in q for w in ("compar", " vs ", "diferencia", "mejor entre")):
            intent = "compare"
        elif any(w in q for w in ("recomiend", "cual compro", "cuál compro", "mejor ")):
            intent = "recommend"
        elif any(w in q for w in ("precio", "barato", "oferta", "euros", "€")):
            intent = "price_check"

        category = "Electrónica"
        for cat, terms in CATEGORY_RULES:
            if any(t in q for t in terms):
                category = cat
                break

        return {
            "raw_query": query,
            "intent": intent,
            "category": category,
            "keywords": [w for w in query.split() if len(w) > 1] or [query],
            "max_price_eur": None,
        }, False
