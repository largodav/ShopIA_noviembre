#!/usr/bin/env zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INFRA_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
TARGET_PLIST="$HOME/Library/LaunchAgents/com.shopia.backend.plist"

mkdir -p "$HOME/Library/LaunchAgents"
sed "s|__INFRA_DIR__|$INFRA_DIR|g" "$SCRIPT_DIR/com.shopia.backend.plist" > "$TARGET_PLIST"

launchctl unload "$TARGET_PLIST" 2>/dev/null || true
launchctl load "$TARGET_PLIST"

echo "Autoarranque de ShopIA instalado en: $TARGET_PLIST"
