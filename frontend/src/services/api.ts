import type { InfoCard, PredictResponse } from "../types/shopia";

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");

const DEMO_CARDS: InfoCard[] = [
  {
    id: "demo-1",
    type: "product",
    title: "Televisor OLED 55\" 4K Smart TV",
    subtitle: "El Corte Inglés · Electrónica",
    summary: "Ejemplo de tarjeta predictiva (modo local sin conexión al backend).",
    price: "1.199 €",
    category: "TV y Vídeo",
    tags: ["OLED", "4K", "HDMI 2.1"],
  },
  {
    id: "demo-2",
    type: "suggestion",
    title: "Comparativa rápida de especificaciones",
    subtitle: "Agente Asesor (v001-b)",
    summary: "Cuando el backend local esté activo, verás aquí respuestas de Ollama en tiempo real.",
    tags: ["Ollama", "Agentes"],
  },
];

export async function fetchPredictions(
  query: string,
  signal?: AbortSignal
): Promise<PredictResponse> {
  const trimmed = query.trim();
  if (!trimmed) {
    return { query: "", version: "v001-b", cards: [] };
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/search/predict?q=${encodeURIComponent(trimmed)}`,
      { signal }
    );
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return (await response.json()) as PredictResponse;
  } catch (err) {
    if ((err as Error).name === "AbortError") {
      throw err;
    }
    const q = trimmed.toLowerCase();
    const filtered = DEMO_CARDS.filter(
      (c) =>
        c.title.toLowerCase().includes(q) ||
        c.summary.toLowerCase().includes(q) ||
        (c.tags || []).some((t) => t.toLowerCase().includes(q))
    );
    return {
      query: trimmed,
      version: "v001-b (offline-demo)",
      cards: filtered.length > 0 ? filtered : DEMO_CARDS,
    };
  }
}
