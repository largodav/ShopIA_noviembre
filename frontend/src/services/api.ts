import type { BackendHealth, ModelsResponse, PredictResponse } from "../types/shopia";
import {
  clearAuthSession,
  enqueueModelSync,
  enqueueSearchSync,
  getAuthToken,
  getSyncQueue,
  removeSyncItems,
  saveCachedSearch,
  searchLocalCatalog,
  setAuthSession,
} from "./localStore";

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");

export class UnauthorizedError extends Error {
  constructor(message = "Autenticación requerida") {
    super(message);
    this.name = "UnauthorizedError";
  }
}

export function getAuthHeaders(): Record<string, string> {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function fetchBackendHealth(): Promise<{
  online: boolean;
  health?: BackendHealth;
}> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), 3500);
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      signal: controller.signal,
      cache: "no-store",
    });
    if (!response.ok) return { online: false };
    const health = (await response.json()) as BackendHealth;
    return { online: true, health };
  } catch {
    return { online: false };
  } finally {
    window.clearTimeout(timer);
  }
}

export async function checkAuthStatus(): Promise<{
  authEnabled: boolean;
  authenticated: boolean;
  offline: boolean;
}> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), 3500);
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/status`, {
      headers: getAuthHeaders(),
      signal: controller.signal,
      cache: "no-store",
    });
    if (!response.ok) {
      return { authEnabled: true, authenticated: false, offline: false };
    }
    const data = (await response.json()) as {
      auth_enabled: boolean;
      authenticated: boolean;
    };
    if (data.auth_enabled && !data.authenticated) {
      clearAuthSession();
    }
    return {
      authEnabled: data.auth_enabled,
      authenticated: data.authenticated,
      offline: false,
    };
  } catch {
    // Offline: keep existing local token valid for local mode
    return {
      authEnabled: true,
      authenticated: Boolean(getAuthToken()),
      offline: true,
    };
  } finally {
    window.clearTimeout(timer);
  }
}

export async function loginWithCredentials(
  username: string,
  password: string
): Promise<{ ok: boolean; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!response.ok) {
      const errData = (await response.json().catch(() => ({}))) as { detail?: string };
      return { ok: false, error: errData.detail || "Credenciales incorrectas." };
    }
    const data = (await response.json()) as {
      access_token: string;
      username: string;
    };
    setAuthSession(data.access_token, data.username);
    return { ok: true };
  } catch {
    return { ok: false, error: "No se pudo conectar con el backend." };
  }
}

export async function fetchLocalModels(): Promise<ModelsResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/models/`, {
      headers: getAuthHeaders(),
    });
    if (response.status === 401) {
      clearAuthSession();
      throw new UnauthorizedError();
    }
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return (await response.json()) as ModelsResponse;
  } catch (err) {
    if (err instanceof UnauthorizedError) throw err;
    return { reachable: false, selected_model: "", models: [] };
  }
}

export async function selectLocalModel(model: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/models/select`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify({ model }),
    });
    if (response.status === 401) {
      clearAuthSession();
      throw new UnauthorizedError();
    }
    return response.ok;
  } catch (err) {
    if (err instanceof UnauthorizedError) throw err;
    enqueueModelSync(model);
    return false;
  }
}

export async function fetchPredictions(
  query: string,
  model?: string,
  signal?: AbortSignal
): Promise<PredictResponse> {
  const trimmed = query.trim();
  if (!trimmed) {
    return { query: "", version: "v003-a", cards: [] };
  }

  try {
    const params = new URLSearchParams({ q: trimmed });
    if (model) params.set("model", model);

    const response = await fetch(
      `${API_BASE_URL}/api/v1/search/predict?${params.toString()}`,
      { signal, headers: getAuthHeaders() }
    );
    if (response.status === 401) {
      clearAuthSession();
      throw new UnauthorizedError();
    }
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = (await response.json()) as PredictResponse;
    saveCachedSearch(trimmed, data.cards);
    return data;
  } catch (err) {
    if ((err as Error).name === "AbortError" || err instanceof UnauthorizedError) {
      throw err;
    }
    enqueueSearchSync(trimmed, model);
    return {
      query: trimmed,
      version: "modo-local",
      offline: true,
      cards: searchLocalCatalog(trimmed),
    };
  }
}

export async function syncPendingQueue(): Promise<{
  synced: number;
  remaining: number;
}> {
  const queue = getSyncQueue();
  if (queue.length === 0) return { synced: 0, remaining: 0 };

  const doneIds: string[] = [];
  for (const item of queue) {
    try {
      if (item.kind === "model" && item.model) {
        const resp = await fetch(`${API_BASE_URL}/api/v1/models/select`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...getAuthHeaders() },
          body: JSON.stringify({ model: item.model }),
        });
        if (resp.ok) doneIds.push(item.id);
      } else if (item.kind === "search" && item.query) {
        const params = new URLSearchParams({ q: item.query });
        if (item.model) params.set("model", item.model);
        const resp = await fetch(
          `${API_BASE_URL}/api/v1/search/predict?${params.toString()}`,
          { headers: getAuthHeaders() }
        );
        if (resp.ok) {
          const data = (await resp.json()) as PredictResponse;
          saveCachedSearch(item.query, data.cards);
          doneIds.push(item.id);
        }
      }
    } catch {
      break;
    }
  }

  removeSyncItems(doneIds);
  const remaining = getSyncQueue().length;
  return { synced: doneIds.length, remaining };
}
