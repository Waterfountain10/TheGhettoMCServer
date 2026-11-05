#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
command -v docker >/dev/null || { echo "Install Docker Engine first"; exit 1; }
docker compose version >/dev/null || { echo "Install Docker Compose plugin first"; exit 1; }
docker info >/dev/null || { echo "Docker inaccessible; reconnect after docker group setup"; exit 1; }
command -v python3 >/dev/null || { echo "Install Python 3"; exit 1; }
[[ "$(uname -m)" == "aarch64" ]] || { echo "Use Raspberry Pi OS Lite 64-bit (aarch64)"; exit 1; }
if [[ ! -f .env ]]; then
  umask 077
  printf 'MC_VERSION=26.3\nMC_MEMORY=1152M\nRCON_PASSWORD=%s\n' "$(python3 -c 'import secrets; print(secrets.token_hex(24))')" > .env
fi
docker compose up -d minecraft
config="data/plugins/Geyser-Spigot/config.yml"
echo "Waiting for Geyser to generate configuration ..."
for _ in $(seq 1 90); do
  [[ -f "$config" ]] && break
  sleep 5
done
if [[ ! -f "$config" ]]; then
  docker compose logs --tail=100 minecraft
  echo "Geyser config not found. Check server/plugin compatibility."
  exit 1
fi
python3 scripts/configure_geyser.py
docker compose restart minecraft
echo "Server started. Check: docker compose logs -f --tail=100 minecraft"
echo "Java TCP 25565; Bedrock TCP+UDP 19132"
