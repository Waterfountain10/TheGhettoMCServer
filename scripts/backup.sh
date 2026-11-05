#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p backups
echo "Stopping server to make a consistent backup ..."
docker compose stop minecraft
restart() { docker compose up -d minecraft; }
trap restart EXIT
archive="backups/minecraft-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "$archive" -C data .
echo "Saved $archive. Keep backups somewhere other than this Pi too."
