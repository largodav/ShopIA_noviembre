# Changelog — ShopIA

Todas las modificaciones relevantes del proyecto se registran aquí.
El control de versiones sigue el esquema `vXXX-letra` (empezando en `v001-a`).

## [v003-b] - 2026-11-25
### Corregido
- **Parser JSON para modelos con múltiples bloques / `<channel|>` (como `g-uncesored:latest`):** `_extract_json_object` ahora extrae bloques ` ```json ` de forma no codiciosa y usa `json.JSONDecoder.raw_decode` para aislar objetos JSON válidos sin fallar cuando el modelo emite varios bloques o etiquetas `<channel|>`.

## [v003-a] - 2026-11-25
### Añadido
- **Identificación de host del backend en `/health` y en la UI:** el endpoint `/health` expone `host: { os, name }` (`BACKEND_HOST_OS`, `BACKEND_HOST_NAME`) y la barra superior muestra el estado en vivo junto al selector de modelo (`Windows · win-home-1` / `Mac` / `Modo local`).
- **Modo local ligero en dispositivo (Android/iOS) + sincronización:** caché de búsquedas y catálogo local en `localStorage`, cola de sincronización automática/manual (`Sincronizar (N)`) al reconectar con el backend y Service Worker `shopia-v003-a` con caché de shell y assets.
- **Autenticación sencilla de usuario único:** `POST /api/v1/auth/login` y `GET /api/v1/auth/status` con tokens HMAC-SHA256 de larga duración (90 días) persistidos en el navegador para no pedir acceso constantemente, manteniendo el modo local operativo sin conexión.
- **Soporte multi-proyecto en Windows:** `BACKEND_PORT=8001` y Tailscale Funnel en `:8443` para convivir con otros servicios locales en `:8000`.

## [v002-b] - 2026-11-25
### Desplegado
- **Tailscale Funnel activo en HTTPS público:** `https://macbook-pro-de-david.tailc0179d.ts.net` conectado al backend local (`:8000`).
- **Publicación en GitHub Pages (`largodav/ShopIA_noviembre`):** repositorio conectado en GitHub, variables de Actions configuradas (`VITE_API_BASE_URL`, `VITE_VAPID_PUBLIC_KEY`, `VITE_BASE_PATH`) y despliegue automático de la PWA en `https://largodav.github.io/ShopIA_noviembre/`.

## [v002-a] - 2026-11-25
### Añadido
- **Detección y selector dinámico de modelos LLM locales (Ollama):**
  - Endpoints `GET /api/v1/models/` (lista todos los modelos instalados en Ollama con tamaño y detalles) y `POST /api/v1/models/select`.
  - Selector minimalista en la barra superior de la PWA para cambiar de modelo al vuelo sin reiniciar Docker.
- **Conector de catálogo de electrónica de El Corte Inglés + PostgreSQL:**
  - `eci_client.py` consulta el buscador público de electrónica de El Corte Inglés (parsing JSON-LD/HTML respetuoso con detección limpia de anti-bot) y almacena/actualiza resultados en la tabla `products`.
  - Nuevos endpoints `POST /api/v1/products/sync` y `POST /api/v1/products/import`, y enlaces directos a El Corte Inglés en las tarjetas.
- **Tailscale Funnel y GitHub Pages (`largodav/ShopIA_noviembre`):**
  - Script `infra/tailscale/setup_funnel.sh` y guía de despliegue en `infra/tailscale/README.md`.
  - `CORS_ORIGINS` preconfigurado para `https://largodav.github.io` y `VITE_BASE_PATH` por defecto en `/ShopIA_noviembre/`.

## [v001-b] - 2026-11-25
### Añadido
- Repositorio Git inicializado en `codigo/` con etiqueta base `v001-a`.
- Cambio de tema claro/oscuro en el frontend PWA con persistencia en `localStorage` y `theme-color` dinámico.
- **PostgreSQL + `pgvector`:** creación automática de extensión `vector` y tablas `products`, `search_history`, `push_subscriptions` y `price_alerts`.
- **Agentes conectados a Ollama:** cliente asíncrono (`ollama_client.py`) configurado por defecto con `gemma4-e2b-uncensored:latest` (parametrizable por rol en `infra/.env`), `IntentAgent` y `AdvisorAgent` con salida JSON estructurada y fallback si Ollama está detenido.
- **Web Push real (VAPID):** endpoints `/api/v1/notifications/vapid-public-key`, `/subscribe`, `/unsubscribe` y `/test` con persistencia en PostgreSQL, script `backend/scripts/generate_vapid.py` y suscripción real `PushManager` desde la PWA.

## [v001-a] - 2026-11-25
### Añadido
- Estructura inicial del proyecto ShopIA dentro de `codigo/`.
- Sistema de versionado (`VERSION`, `CHANGELOG.md`).
- Esqueleto del **Frontend PWA** (Vite + React + TypeScript) con:
  - Interfaz minimalista: campo de texto predictivo con borde inferior en tonos blancos.
  - Tarjetas dinámicas bajo el cuadro de texto (datos de ejemplo para validación inicial).
  - Manifiesto PWA (`manifest.webmanifest`), iconos y Service Worker base (`sw.ts`) listo para instalación y Web Push.
- Esqueleto del **Backend** (Python + FastAPI) con:
  - Endpoint `/health` y `/api/v1/search/predict` de prueba.
  - Estructura modular para `agents/` (orquestador, intención, El Corte Inglés, asesor), `services/`, `models/` y `api/routes/`.
- **Infraestructura (`infra/`):**
  - `docker-compose.yml` con PostgreSQL (`pgvector`), backend FastAPI y perfiles opcionales `nvidia` (Ollama con GPU NVIDIA en Windows) y `tailscale` (Tailscale Funnel HTTPS).
  - Soporte por defecto para Ollama nativo en host (`host.docker.internal:11434`) para Mac con Apple Silicon y Windows.
  - Scripts de autoarranque para macOS (`launchd`) y Windows (Programador de Tareas).
- Workflow de GitHub Actions (`.github/workflows/deploy-pages.yml`) para publicar la PWA en GitHub Pages.
