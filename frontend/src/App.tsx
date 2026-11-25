import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { PredictiveInput } from "./components/PredictiveInput/PredictiveInput";
import { InfoCards } from "./components/InfoCards/InfoCards";
import {
  checkAuthStatus,
  fetchBackendHealth,
  fetchLocalModels,
  fetchPredictions,
  loginWithCredentials,
  selectLocalModel,
  syncPendingQueue,
  UnauthorizedError,
} from "./services/api";
import {
  clearAuthSession,
  getAuthToken,
  getSyncQueue,
} from "./services/localStore";
import {
  isNotificationSupported,
  subscribeToWebPush,
  triggerBackendTestPush,
} from "./services/notifications";
import type { BackendHealth, InfoCard, LocalModel } from "./types/shopia";

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

  const [backendOnline, setBackendOnline] = useState<boolean>(false);
  const [backendHealth, setBackendHealth] = useState<BackendHealth | null>(null);
  const wasOnlineRef = useRef<boolean>(false);

  const [authEnabled, setAuthEnabled] = useState<boolean>(true);
  const [authenticated, setAuthenticated] = useState<boolean>(() => Boolean(getAuthToken()));
  const [loginUser, setLoginUser] = useState("david");
  const [loginPass, setLoginPass] = useState("");
  const [loginError, setLoginError] = useState("");
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  const [models, setModels] = useState<LocalModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>(
    () => window.localStorage.getItem(MODEL_STORAGE_KEY) || ""
  );
  const [pendingSyncCount, setPendingSyncCount] = useState<number>(() => getSyncQueue().length);
  const [isSyncing, setIsSyncing] = useState(false);

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

  const loadModels = useCallback(async () => {
    try {
      const res = await fetchLocalModels();
      setModels(res.models);
      const saved = window.localStorage.getItem(MODEL_STORAGE_KEY);
      const validSaved = saved && res.models.some((m) => m.name === saved) ? saved : "";
      const initial = validSaved || res.selected_model || res.models[0]?.name || "";
      if (initial) {
        setSelectedModel(initial);
        window.localStorage.setItem(MODEL_STORAGE_KEY, initial);
        if (validSaved && validSaved !== res.selected_model) {
          await selectLocalModel(validSaved);
        }
      }
    } catch (err) {
      if (err instanceof UnauthorizedError) {
        setAuthenticated(false);
      }
    }
  }, []);

  const handleSyncNow = useCallback(async () => {
    if (isSyncing) return;
    setIsSyncing(true);
    try {
      const { remaining } = await syncPendingQueue();
      setPendingSyncCount(remaining);
    } finally {
      setIsSyncing(false);
    }
  }, [isSyncing]);

  const refreshBackendState = useCallback(async () => {
    const { online, health } = await fetchBackendHealth();
    setBackendOnline(online);
    setBackendHealth(health || null);

    if (online && health) {
      setAuthEnabled(health.auth_enabled ?? true);
      const auth = await checkAuthStatus();
      setAuthEnabled(auth.authEnabled);
      setAuthenticated(auth.authenticated);

      if (auth.authenticated) {
        if (!wasOnlineRef.current) {
          await loadModels();
          if (getSyncQueue().length > 0) {
            await handleSyncNow();
          }
        }
      }
    }
    wasOnlineRef.current = online;
  }, [handleSyncNow, loadModels]);

  useEffect(() => {
    refreshBackendState();
    const interval = window.setInterval(refreshBackendState, 20000);
    const onOnline = () => refreshBackendState();
    const onOffline = () => {
      setBackendOnline(false);
      wasOnlineRef.current = false;
    };
    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.clearInterval(interval);
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
  }, [refreshBackendState]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  const handleModelChange = async (nextModel: string) => {
    setSelectedModel(nextModel);
    window.localStorage.setItem(MODEL_STORAGE_KEY, nextModel);
    try {
      await selectLocalModel(nextModel);
      setPendingSyncCount(getSyncQueue().length);
    } catch (err) {
      if (err instanceof UnauthorizedError) {
        setAuthenticated(false);
      }
    }
  };

  const handleLoginSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoginError("");
    setIsLoggingIn(true);
    try {
      const res = await loginWithCredentials(loginUser, loginPass);
      if (!res.ok) {
        setLoginError(res.error || "No se pudo iniciar sesión.");
        return;
      }
      setAuthenticated(true);
      setLoginPass("");
      await loadModels();
      if (getSyncQueue().length > 0) {
        await handleSyncNow();
      }
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleLogout = () => {
    clearAuthSession();
    setAuthenticated(false);
    setCards([]);
    setQuery("");
  };

  useEffect(() => {
    const needsLogin = backendOnline && authEnabled && !authenticated;
    if (needsLogin) return;

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
        setPendingSyncCount(getSyncQueue().length);
        if (result.offline) {
          setBackendOnline(false);
        }
      } catch (err) {
        if (err instanceof UnauthorizedError) {
          setAuthenticated(false);
        } else if ((err as Error).name !== "AbortError") {
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
  }, [query, selectedModel, backendOnline, authEnabled, authenticated]);

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

  const hostLabel = backendOnline
    ? backendHealth?.host?.os
      ? `${backendHealth.host.os}${backendHealth.host.name ? ` · ${backendHealth.host.name}` : ""}`
      : "Backend activo"
    : "Modo local";

  const hostTitle = backendOnline
    ? `Conectado a ${backendHealth?.host?.os || "Backend"} (${backendHealth?.version || ""}) · Ollama: ${
        backendHealth?.ollama?.reachable ? "activo" : "sin conexión"
      }`
    : "Sin conexión al backend. Usando caché local en este dispositivo.";

  const needsLogin = backendOnline && authEnabled && !authenticated;

  return (
    <div className="app-shell">
      <header className="top-bar">
        <span className="brand-meta">ShopIA · {backendHealth?.version || "v003-a"}</span>
        <div className="top-bar-actions">
          <span
            className={`status-pill ${backendOnline ? "is-online" : "is-offline"}`}
            title={hostTitle}
          >
            <span className="status-dot" />
            {hostLabel}
          </span>
          {pendingSyncCount > 0 && (
            <button
              type="button"
              className="pill-button"
              onClick={handleSyncNow}
              disabled={!backendOnline || isSyncing}
              title={
                backendOnline
                  ? "Sincronizar consultas guardadas en modo local"
                  : "Se sincronizará al recuperar conexión"
              }
            >
              {isSyncing ? "Sincronizando..." : `Sincronizar (${pendingSyncCount})`}
            </button>
          )}
          {models.length > 0 && !needsLogin && (
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
            !needsLogin &&
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
          {authEnabled && authenticated && (
            <button
              type="button"
              className="pill-button"
              onClick={handleLogout}
              title="Cerrar sesión en este dispositivo"
            >
              Salir
            </button>
          )}
        </div>
      </header>

      <main className="main-stage">
        {needsLogin ? (
          <form className="auth-card" onSubmit={handleLoginSubmit}>
            <h1 className="auth-title">Acceso a ShopIA</h1>
            <p className="auth-subtitle">
              Inicia sesión una vez; tu dispositivo recordará la sesión.
            </p>
            <input
              type="text"
              className="auth-input"
              placeholder="Usuario"
              value={loginUser}
              onChange={(e) => setLoginUser(e.target.value)}
              autoComplete="username"
              required
            />
            <input
              type="password"
              className="auth-input"
              placeholder="Contraseña"
              value={loginPass}
              onChange={(e) => setLoginPass(e.target.value)}
              autoComplete="current-password"
              required
            />
            {loginError && <p className="auth-error">{loginError}</p>}
            <button type="submit" className="auth-submit" disabled={isLoggingIn}>
              {isLoggingIn ? "Entrando..." : "Entrar"}
            </button>
          </form>
        ) : (
          <>
            <PredictiveInput value={query} onChange={setQuery} isLoading={isLoading} />
            <InfoCards cards={cards} />
          </>
        )}
      </main>
    </div>
  );
}

export default App;
