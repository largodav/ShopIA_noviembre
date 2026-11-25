# ShopIA

Aplicación Web Progresiva (PWA) instalable con notificaciones del sistema, orientada a recoger peticiones del usuario y mostrar/procesar información sobre productos de electrónica de **El Corte Inglés**, impulsada por un backend local con **Ollama + sistema de Agentes + PostgreSQL (`pgvector`)**.

- **Versión actual:** `v001-a` (ver [VERSION](./VERSION) y [CHANGELOG.md](./CHANGELOG.md)).

## Arquitectura

| Capa | Tecnología | Despliegue |
| :--- | :--- | :--- |
| **Frontend (PWA)** | Vite + React + TypeScript + Service Worker | GitHub Pages (HTTPS) |
| **Backend + Agentes** | Python + FastAPI + Ollama | Local en Docker (Mac Apple Silicon / Windows NVIDIA) |
| **Base de Datos** | PostgreSQL + `pgvector` | Contenedor Docker |
| **Exposición Pública** | Tailscale Funnel (HTTPS automático) | Host o perfil `--profile tailscale` |

## Estructura del proyecto

```text
codigo/
├── VERSION
├── CHANGELOG.md
├── .github/workflows/deploy-pages.yml
├── frontend/          # PWA minimalista (input predictivo + tarjetas + notificaciones)
├── backend/           # API FastAPI + Agentes Ollama + cliente ECI + Web Push
└── infra/             # Docker Compose (Mac Silicon / Windows NVIDIA), Tailscale y autoarranque
```

## Inicio rápido (desarrollo local)

### 1. Variables de entorno
```bash
cp infra/.env.example infra/.env
```

### 2. Levantar el backend en Docker
- **En Mac (Apple Silicon) o Windows con Ollama nativo en el host:**
  ```bash
  docker compose -f infra/docker-compose.yml --env-file infra/.env up -d --build
  ```
- **En Windows con GPU NVIDIA (Ollama dentro de Docker):**
  ```bash
  docker compose -f infra/docker-compose.yml --env-file infra/.env --profile nvidia up -d --build
  ```
- **Añadir Tailscale en contenedor (opcional, si no usas Tailscale instalado en el host):**
  ```bash
  docker compose -f infra/docker-compose.yml --env-file infra/.env --profile tailscale up -d
  ```

### 3. Ejecutar el frontend en desarrollo
```bash
cd frontend
npm install
npm run dev
```

## Exposición pública con Tailscale Funnel

Si tienes Tailscale instalado en el equipo host:
```bash
tailscale funnel --bg 8000
```
Esto expondrá `http://localhost:8000` en una URL pública HTTPS `https://<tu-maquina>.<tu-tailnet>.ts.net`, que podrás configurar como `VITE_API_BASE_URL` en el frontend/GitHub Pages.

## Autoarranque

Consulta [infra/autostart/README.md](./infra/autostart/README.md) para configurar el arranque automático en **macOS** (`launchd`) y **Windows** (Programador de Tareas).
