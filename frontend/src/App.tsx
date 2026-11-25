import { useEffect, useState } from "react";
import { PredictiveInput } from "./components/PredictiveInput/PredictiveInput";
import { InfoCards } from "./components/InfoCards/InfoCards";
import { fetchLocalModels, fetchPredictions, selectLocalModel } from "./services/api";
import {
  isNotificationSupported,
  subscribeToWebPush,
  triggerBackendTestPush,
} from "./services/notifications";
import type { InfoCard, LocalModel } from "./types/shopia";

type Theme = "dark" | "light";

const THEME_STORAGE_KEY = "shopia-theme";
const MODEL_STORAGE_KEY = "shopia-model";

function getInitialTheme(): Theme {
  const saved = window.localStorage.getItem(THEME_STORAGE_KEY);
  if (saved === "dark" || saved === "light") return saved;
  return window.matchMedia?.("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

export function App() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);
  const [query, setQuery] = useState("");
  const [cards, setCards] = useState<InfoCard[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [models, setModels] = useState<LocalModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>(
    () => window.localStorage.getItem(MODEL_STORAGE_KEY) || ""
  );
  const [notifStatus, setNotifStatus] = useState<NotificationPermission>(
    isNotificationSupported() ? Notification.permission : "denied"
  );
  const [pushSubscribed, setPushSubscribed] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
    const metaTheme = document.querySelector('meta[name="theme-color"]');
    if (metaTheme) {
      metaTheme.setAttribute("content", theme === "dark" ? "#0b0c10" : "#f3f4f7");
    }
  }, [theme]);

  useEffect(() => {
    let active = true;
    fetchLocalModels().then((res) => {
      if (!active) return;
      setModels(res.models);
      const saved = window.localStorage.getItem(MODEL_STORAGE_KEY);
      const validSaved = saved && res.models.some((m) => m.name === saved) ? saved : "";
      const initial = validSaved || res.selected_model || res.models[0]?.name || "";
      if (initial) {
        setSelectedModel(initial);
        window.localStorage.setItem(MODEL_STORAGE_KEY, initial);
        if (validSaved && validSaved !== res.selected_model) {
          selectLocalModel(validSaved);
        }
      }
    });
    return () => {
      active = false;
    };
  }, []);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  const handleModelChange = async (nextModel: string) => {
    setSelectedModel(nextModel);
    window.localStorage.setItem(MODEL_STORAGE_KEY, nextModel);
    await selectLocalModel(nextModel);
  };

  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < 3) {
      setCards([]);
      setIsLoading(false);
      return;
    }

    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      setIsLoading(true);
      try {
        const result = await fetchPredictions(
          trimmed,
          selectedModel || undefined,
          controller.signal
        );
        setCards(result.cards);
      } catch (err) {
        if ((err as Error).name !== "AbortError") {
          console.error("Error obteniendo predicciones:", err);
        }
      } finally {
        setIsLoading(false);
      }
    }, 600);

    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [query, selectedModel]);

  const handleEnableNotifications = async () => {
    const { permission, subscribed } = await subscribeToWebPush();
    setNotifStatus(permission);
    setPushSubscribed(subscribed);
    if (subscribed) {
      await triggerBackendTestPush();
    }
  };

  const handleTestPush = async () => {
    if (!pushSubscribed) {
      const { subscribed } = await subscribeToWebPush();
      setPushSubscribed(subscribed);
    }
    await triggerBackendTestPush();
  };

  return (
    <div className="app-shell">
      <header className="top-bar">
        <span className="brand-meta">ShopIA · v002-a</span>
        <div className="top-bar-actions">
          {models.length > 0 && (
            <select
              className="pill-select"
              value={selectedModel}
              onChange={(e) => handleModelChange(e.target.value)}
              aria-label="Seleccionar modelo LLM local"
              title="Modelo LLM local (Ollama)"
            >
              {models.map((m) => (
                <option key={m.name} value={m.name}>
                  {m.name}
                  {m.size_gb ? ` (${m.size_gb} GB)` : ""}
                </option>
              ))}
            </select>
          )}
          <button
            type="button"
            className="pill-button"
            onClick={toggleTheme}
            aria-label={theme === "dark" ? "Cambiar a tema claro" : "Cambiar a tema oscuro"}
          >
            {theme === "dark" ? "Tema claro" : "Tema oscuro"}
          </button>
          {isNotificationSupported() &&
            (notifStatus === "granted" ? (
              <button type="button" className="pill-button" onClick={handleTestPush}>
                Probar Push
              </button>
            ) : (
              <button
                type="button"
                className="pill-button"
                onClick={handleEnableNotifications}
              >
                Activar notificaciones
              </button>
            ))}
        </div>
      </header>

      <main className="main-stage">
        <PredictiveInput value={query} onChange={setQuery} isLoading={isLoading} />
        <InfoCards cards={cards} />
      </main>
    </div>
  );
}

export default App;
