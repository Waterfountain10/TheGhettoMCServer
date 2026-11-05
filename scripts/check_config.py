#!/usr/bin/env python3
"""Dependency-free static sanity checks; does not start Minecraft."""
from pathlib import Path
import unittest

root = Path(__file__).resolve().parents[1]
compose = (root / "docker-compose.yml").read_text()
bootstrap = (root / "scripts/bootstrap.sh").read_text()
ignore = (root / ".gitignore").read_text()

assert 'TYPE: "PAPER"' in compose
assert 'VERSION: "${MC_VERSION:-26.3}"' in compose
assert 'MAX_PLAYERS: "3"' in compose
assert '"19132:19132/tcp"' in compose and '"19132:19132/udp"' in compose
assert '"25565:25565/tcp"' in compose
assert "geyser" in compose.lower() and "floodgate" in compose.lower()
assert "1152M" in compose
assert "MC_VERSION=26.3" in bootstrap
assert "mc.kiem.net" in compose
assert ".env" in ignore and "data/" in ignore and "backups/" in ignore
print("PASS: static crossplay, resource, and secret checks")
