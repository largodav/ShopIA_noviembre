# Changelog — ShopIA

Todas las modificaciones relevantes del proyecto se registran aquí.
El control de versiones sigue el esquema `vXXX-letra` (empezando en `v001-a`).

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
