#!/usr/bin/env zsh
set -euo pipefail

PORT="${1:-8000}"

if ! command -v tailscale >/dev/null 2>&1; then
  echo "Tailscale CLI no encontrado. Instálalo o añade el binario al PATH."
  exit 1
fi

echo "Activando Tailscale Funnel en HTTPS -> http://127.0.0.1:${PORT} ..."
tailscale funnel --bg "${PORT}"

echo ""
echo "Estado actual de Tailscale Funnel:"
tailscale funnel status
