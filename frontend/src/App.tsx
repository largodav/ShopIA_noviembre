import { useEffect, useState } from "react";
import { PredictiveInput } from "./components/PredictiveInput/PredictiveInput";
import { InfoCards } from "./components/InfoCards/InfoCards";
import { fetchPredictions } from "./services/api";
import {
  isNotificationSupported,
  subscribeToWebPush,
  triggerBackendTestPush,
} from "./services/notifications";
import type { InfoCard } from "./types/shopia";

type Theme = "dark" | "light";

const THEME_STORAGE_KEY = "shopia-theme";

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

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
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
        const result = await fetchPredictions(trimmed, controller.signal);
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
  }, [query]);

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
        <span className="brand-meta">ShopIA · v001-b</span>
        <div className="top-bar-actions">
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
