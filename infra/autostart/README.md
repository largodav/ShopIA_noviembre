# Autoarranque de ShopIA (macOS y Windows)

Los contenedores de `infra/docker-compose.yml` tienen `restart: always`, por lo que basta con que Docker arranque al iniciar el equipo y ejecute `docker compose up -d`.

## macOS (Apple Silicon)

1. Asegúrate de tener **Ollama** y **Docker Desktop** (o OrbStack/Colima) configurados para iniciar al arrancar sesión.
2. Ejecuta el instalador del agente `launchd`:
   ```bash
   chmod +x infra/autostart/macos/install_autostart.sh
   ./infra/autostart/macos/install_autostart.sh
   ```

## Windows (con GPU NVIDIA)

1. Asegúrate de tener **Docker Desktop** con backend WSL2 y soporte NVIDIA habilitado al inicio.
2. Abre PowerShell como administrador y ejecuta:
   ```powershell
   # Modo estándar (Ollama nativo en Windows)
   .\infra\autostart\windows\install_autostart.ps1

   # Modo GPU NVIDIA en Docker (--profile nvidia)
   .\infra\autostart\windows\install_autostart.ps1 -UseNvidiaProfile
   ```
