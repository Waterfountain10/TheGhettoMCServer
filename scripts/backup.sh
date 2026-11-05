#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p backups
chmod 700 backups
if [[ ! -d data || ! -f data/server.properties ]]; then
  echo "No initialized Minecraft world found in data/; refusing empty backup" >&2
  exit 1
fi
# Stop cleanly; restart on any subsequent error. Never create a misleading partial archive.
docker compose stop -t 90 minecraft
restart() { docker compose up -d minecraft; }
trap restart EXIT
archive="backups/minecraft-$(date -u +%Y%m%dT%H%M%SZ).tar.gz"
tmp="${archive}.partial"
cleanup() { rm -f "$tmp"; restart; }
trap cleanup EXIT
tar -czf "$tmp" -C data .
tar -tzf "$tmp" >/dev/null
mv "$tmp" "$archive"
chmod 600 "$archive"
echo "Verified backup: $archive"
echo "Copy encrypted backups off the Pi; local backups do not survive SD-card failure."
