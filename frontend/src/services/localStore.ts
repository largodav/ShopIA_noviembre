import type { InfoCard, SyncQueueItem } from "../types/shopia";

const AUTH_TOKEN_KEY = "shopia-auth-token";
const AUTH_USER_KEY = "shopia-auth-user";
const CACHE_QUERIES_KEY = "shopia-local-queries";
const CACHE_CATALOG_KEY = "shopia-local-catalog";
const SYNC_QUEUE_KEY = "shopia-sync-queue";

const MAX_CACHED_QUERIES = 40;
const MAX_CATALOG_ITEMS = 100;

interface CachedQueryEntry {
  query: string;
  cards: InfoCard[];
  updatedAt: number;
}

const DEMO_CARDS: InfoCard[] = [
  {
    id: "demo-1",
    type: "product",
    title: 'Televisor OLED 55" 4K Smart TV',
    subtitle: "El Corte Inglés · Electrónica",
    summary: "Ejemplo guardado en modo local ligero (sin conexión al backend).",
    price: "1.199 €",
    category: "TV y Vídeo",
    tags: ["OLED", "4K", "HDMI 2.1"],
  },
  {
    id: "demo-2",
    type: "suggestion",
    title: "Búsqueda guardada para sincronizar",
    subtitle: "Modo local en dispositivo",
    summary:
      "Tu consulta se ha guardado en este dispositivo y se sincronizará automáticamente cuando vuelva la conexión con el backend.",
    tags: ["Modo local", "Sync"],
  },
];

function readJson<T>(key: string, fallback: T): T {
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function writeJson(key: string, value: unknown): void {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Ignore quota errors on constrained mobile storage
  }
}

export function getAuthToken(): string {
  return window.localStorage.getItem(AUTH_TOKEN_KEY) || "";
}

export function getAuthUsername(): string {
  return window.localStorage.getItem(AUTH_USER_KEY) || "";
}

export function setAuthSession(token: string, username: string): void {
  window.localStorage.setItem(AUTH_TOKEN_KEY, token);
  window.localStorage.setItem(AUTH_USER_KEY, username);
}

export function clearAuthSession(): void {
  window.localStorage.removeItem(AUTH_TOKEN_KEY);
  window.localStorage.removeItem(AUTH_USER_KEY);
}

export function saveCachedSearch(query: string, cards: InfoCard[]): void {
  const normalized = query.trim().toLowerCase();
  if (!normalized || cards.length === 0) return;

  const queries = readJson<Record<string, CachedQueryEntry>>(CACHE_QUERIES_KEY, {});
  queries[normalized] = { query: query.trim(), cards, updatedAt: Date.now() };
  const entries = Object.entries(queries)
    .sort((a, b) => b[1].updatedAt - a[1].updatedAt)
    .slice(0, MAX_CACHED_QUERIES);
  writeJson(CACHE_QUERIES_KEY, Object.fromEntries(entries));

  const catalog = readJson<InfoCard[]>(CACHE_CATALOG_KEY, []);
  const byId = new Map<string, InfoCard>();
  for (const card of cards) {
    if (card.type === "product" || card.sourceUrl || card.price) {
      byId.set(card.id, card);
    }
  }
  for (const existing of catalog) {
    if (!byId.has(existing.id)) {
      byId.set(existing.id, existing);
    }
  }
  writeJson(CACHE_CATALOG_KEY, Array.from(byId.values()).slice(0, MAX_CATALOG_ITEMS));
}

export function searchLocalCatalog(query: string): InfoCard[] {
  const normalized = query.trim().toLowerCase();
  const queries = readJson<Record<string, CachedQueryEntry>>(CACHE_QUERIES_KEY, {});
  if (queries[normalized]?.cards?.length) {
    return queries[normalized].cards;
  }

  const catalog = readJson<InfoCard[]>(CACHE_CATALOG_KEY, []);
  const pool = [...catalog, ...DEMO_CARDS];
  const terms = normalized.split(/\s+/).filter(Boolean);

  const matched = pool.filter((card) => {
    const haystack = [
      card.title,
      card.subtitle || "",
      card.summary,
      card.category || "",
      ...(card.tags || []),
    ]
      .join(" ")
      .toLowerCase();
    return terms.some((t) => haystack.includes(t));
  });

  if (matched.length > 0) {
    return matched.slice(0, 6);
  }
  return DEMO_CARDS;
}

export function getSyncQueue(): SyncQueueItem[] {
  return readJson<SyncQueueItem[]>(SYNC_QUEUE_KEY, []);
}

export function enqueueSearchSync(query: string, model?: string): void {
  const trimmed = query.trim();
  if (trimmed.length < 3) return;
  const queue = getSyncQueue();
  const exists = queue.some(
    (item) => item.kind === "search" && item.query?.toLowerCase() === trimmed.toLowerCase()
  );
  if (exists) return;
  queue.push({
    id: `search-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    kind: "search",
    query: trimmed,
    model,
    createdAt: Date.now(),
  });
  writeJson(SYNC_QUEUE_KEY, queue.slice(-30));
}

export function enqueueModelSync(model: string): void {
  if (!model) return;
  const queue = getSyncQueue().filter((item) => item.kind !== "model");
  queue.push({
    id: `model-${Date.now()}`,
    kind: "model",
    model,
    createdAt: Date.now(),
  });
  writeJson(SYNC_QUEUE_KEY, queue);
}

export function removeSyncItems(ids: string[]): void {
  if (ids.length === 0) return;
  const idSet = new Set(ids);
  const next = getSyncQueue().filter((item) => !idSet.has(item.id));
  writeJson(SYNC_QUEUE_KEY, next);
}
