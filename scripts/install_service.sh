#!/bin/bash
# Instala el service systemd en una Raspberry Pi (ejecutar como root)
set -euo pipefail

SERVICE_NAME=sistema-biometrico.service
DEPLOY_PATH="/etc/systemd/system/$SERVICE_NAME"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ "$EUID" -ne 0 ]; then
  echo "Ejecuta como root: sudo ./install_service.sh"
  exit 1
fi

cp "$PROJECT_DIR/deploy/$SERVICE_NAME" "$DEPLOY_PATH"
chmod 644 "$DEPLOY_PATH"
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"
echo "Service $SERVICE_NAME instalado y arrancado."
