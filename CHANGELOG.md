# Changelog — ShopIA

Todas las modificaciones relevantes del proyecto se registran aquí.
El control de versiones sigue el esquema `vXXX-letra` (empezando en `v001-a`).

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
