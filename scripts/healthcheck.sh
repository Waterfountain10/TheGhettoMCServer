#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
echo "=== $(date -Is) ==="
echo "--- Memory ---"
free -h || true
echo "--- Disk ---"
df -h . || true
echo "--- Pi thermal / power ---"
if command -v vcgencmd >/dev/null 2>&1; then
  vcgencmd measure_temp || true
  vcgencmd get_throttled || true
fi
echo "--- Container ---"
docker compose ps || true
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}' || true
echo "--- Players ---"
docker compose exec -T minecraft rcon-cli list || true
echo "--- Tick rate ---"
docker compose exec -T minecraft rcon-cli tps || true
echo "--- Recent server warnings ---"
docker compose logs --tail=250 minecraft | grep -Ei 'warn|error|exception|outofmemory|can.t keep up|failed' | tail -35 || true
echo "--- Listening ports (if ss installed) ---"
command -v ss >/dev/null && ss -lntup | grep -E '(:25565|:19132)' || true
