#!/usr/bin/env python3
"""Idempotently configure Geyser's generated YAML for NetherNet/Floodgate."""
from pathlib import Path
import re
import sys

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "data/plugins/Geyser-Spigot/config.yml"

def configure(text: str) -> str:
    match = re.search(r"(?m)^bedrock:\s*\n", text)
    if not match:
        raise ValueError("Geyser config has no top-level bedrock: section")
    next_section = re.search(r"(?m)^[A-Za-z][A-Za-z0-9_-]*:\s*(?:#.*)?$", text[match.end():])
    end = match.end() + next_section.start() if next_section else len(text)
    body = text[match.end():end]

    def set_setting(section: str, key: str, value: str) -> str:
        pattern = rf"(?m)^(\s+)({re.escape(key)}):\s*[^\n]*$"
        if re.search(pattern, section):
            return re.sub(pattern, lambda m: f"{m.group(1)}{key}: {value}", section, count=1)
        return f"  {key}: {value}\n" + section

    body = set_setting(body, "port", "19132")
    body = set_setting(body, "transport", "nethernet")
    text = text[:match.end()] + body + text[end:]
    auth_pattern = r"(?m)^(\s*)auth-type:\s*[^\n]*$"
    if not re.search(auth_pattern, text):
        raise ValueError("No auth-type found; check generated Geyser schema")
    return re.sub(auth_pattern, lambda m: f"{m.group(1)}auth-type: floodgate", text, count=1)

def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CONFIG
    if not path.exists():
        print(f"Missing Geyser config: {path}", file=sys.stderr)
        return 1
    try:
        original = path.read_text()
        updated = configure(original)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if original != updated:
        path.write_text(updated)
    print("Geyser configured: NetherNet TCP+UDP 19132; Floodgate authentication.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
