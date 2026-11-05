# mcctl: Zig management CLI

Small optional Zig command wrapper for the Minecraft server. It is **not** a Minecraft server implementation. It invokes Docker Compose, so run it from the **repository root** on the Pi.

Tested target design: Linux ARM64 / Raspberry Pi OS Lite 64-bit. Source targets Zig 0.15.x APIs; compilation has not yet been tested on the Pi.

Install a matching Zig compiler from https://ziglang.org/download/ then:

```bash
cd zig
zig build -Doptimize=ReleaseSmall
cd ..
./zig/zig-out/bin/mcctl status
./zig/zig-out/bin/mcctl logs
./zig/zig-out/bin/mcctl players
./zig/zig-out/bin/mcctl restart
./zig/zig-out/bin/mcctl backup
```

SSH from iPhone over Tailscale for remote use. The CLI runs no permanent daemon and uses essentially no RAM while idle.
