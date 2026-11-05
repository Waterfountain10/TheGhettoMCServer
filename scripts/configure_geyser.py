#!/usr/bin/env python3
"""Configure generated Geyser-Spigot YAML without discarding other settings."""
from pathlib import Path
import re
import sys

config = Path(__file__).resolve().parent.parent / "data/plugins/Geyser-Spigot/config.yml"
if not config.exists():
    sys.exit(f"Missing {config}; let Minecraft start and generate the config first.")
text = config.read_text()
before = text

# Only edit the top-level bedrock section; preserve Geyser's other settings.
match = re.search(r"(?m)^bedrock:\s*\n", text)
if not match:
    sys.exit("Geyser config has no top-level 'bedrock:' section; update manually.")
next_section = re.search(r"(?m)^[A-Za-z][A-Za-z0-9_-]*:\s*(?:#.*)?$", text[match.end():])
end = match.end() + next_section.start() if next_section else len(text)
body = text[match.end():end]
def set_setting(section, key, value):
    pattern = rf"(?m)^(\s+)({re.escape(key)}):\s*[^\n]*$"
    if re.search(pattern, section):
        return re.sub(pattern, lambda m: f"{m.group(1)}{key}: {value}", section, count=1)
    return f"  {key}: {value}\n" + section
body = set_setting(body, "port", "19132")
body = set_setting(body, "transport", "nethernet")
text = text[:match.end()] + body + text[end:]

# Floodgate authentication can be under 'java:' (newer) or 'remote:' (older).
auth_pattern = r"(?m)^(\s*)auth-type:\s*[^\n]*$"
if not re.search(auth_pattern, text):
    sys.exit("No auth-type setting found. Inspect Geyser config and set it to floodgate manually.")
text = re.sub(auth_pattern, lambda m: f"{m.group(1)}auth-type: floodgate", text, count=1)

if text != before:
    config.write_text(text)
    print("Configured Geyser: TCP+UDP 19132, nethernet transport, floodgate authentication.")
else:
    print("Geyser settings are already correct.")
