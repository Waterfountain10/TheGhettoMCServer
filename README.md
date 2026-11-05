# Minecraft crossplay on Raspberry Pi 4B (2 GB)

**Status: source/configuration only. Not deployed or performance-tested.** This project runs a Paper Java server with GeyserMC and Floodgate so Java (Mac) and Bedrock (iPad/Windows) can join the same world. GitHub stores the setup; the world runs on your Raspberry Pi. Zig is used for a small optional local management CLI, not to reimplement Minecraft.

## Hardware and limits

Raspberry Pi 4 Model B, **2 GB RAM**, 64 GB microSD, optional Waveshare 3.5-inch SPI LCD, fan and 5V/3A power supply. Use Raspberry Pi OS Lite **64-bit** and Ethernet if possible. **Do not install a desktop GUI or touchscreen drivers yet.** This is an experimental low-memory setup: start with **three players**, with no spare capacity, and expect lag during exploration/chunk generation. If performance is unacceptable, upgrade to a Pi 5 with 8 GB or a cloud VM. Back up worlds off the SD card.

## A. First-time Pi setup (requires physical access to the SD card and a computer)

1. Get a microSD reader and a computer (Mac, Windows, Linux). Install [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2. Choose **Raspberry Pi 4**, **Raspberry Pi OS Lite (64-bit)**, and the 64 GB microSD card. All data on the selected card will be erased.
3. In OS customization, set a username (e.g. `mcadmin`), a strong password, hostname `minecraftpi`, Wi-Fi country/SSID/password if not using Ethernet, and **enable SSH with password authentication** (prefer SSH public keys when possible). Configure locale/timezone.
4. Write and verify the card. Insert it into the Pi. Connect Ethernet (recommended), power and fan. The Waveshare LCD is optional; leave it off until Minecraft is stable.
5. Connect your iPhone to the **same home Wi-Fi**. In Termius/Blink, SSH to `mcadmin@minecraftpi.local` (replace username). If name resolution fails, find the Pi's LAN IP in your router's device list and SSH to that IP.
6. Once logged in, run:
```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y git curl python3 ca-certificates
sudo reboot
```
Reconnect after reboot.

## B. Docker installation (on Pi)

Follow the official [Docker Engine Debian instructions](https://docs.docker.com/engine/install/debian/) for your Raspberry Pi OS version. Install Docker Engine and the Compose plugin. Verify with `sudo docker version` and `sudo docker compose version`. To run Docker without sudo, run `sudo usermod -aG docker "$USER"`, log out and reconnect. **Docker group grants root-equivalent privileges.**

## C. Download and start

This repository is currently public. On the Pi, clone it directly (no GitHub token required):

```bash
git clone https://github.com/Waterfountain10/TheGhettoMCServer.git
cd TheGhettoMCServer
bash scripts/bootstrap.sh
```

Then inspect the logs:

```bash
docker compose logs --tail=100 minecraft
```

The bootstrap script creates a secret `.env`, downloads Paper and the plugins, waits for Geyser's config, sets `auth-type: floodgate` and `transport: nethernet`, and restarts Minecraft. The **default heap is 1152 MB**. No dashboard container runs by default. If Paper's latest version requires too much memory or is incompatible, pin `MC_VERSION` in `.env` to a mutually supported version and retry. First launch can be slow.

## D. Connect your friends

On the same LAN: Java Mac -> server address `PI_LAN_IP:25565`; Bedrock iPad or Windows -> `PI_LAN_IP` port `19132`. For internet play, configure your router's DHCP reservation and forward **TCP 25565** (Java) and **TCP + UDP 19132** (Bedrock) to the Pi. Check whether your ISP uses CGNAT; if so, use a Geyser-compatible TCP/UDP tunnel. Never expose RCON or SSH publicly. Geyser's newer NetherNet transport may require an initial Bedrock trust/signaling step; see the [official setup docs](https://geysermc.org/wiki/geyser/setup/).

## E. Admin from iPhone, privately

Install [Tailscale](https://tailscale.com/download/linux) on the Pi and iPhone; sign into the same tailnet, run `sudo tailscale up` on the Pi, then use an iPhone SSH app to connect to its Tailscale IP. No public admin dashboard is exposed, saving RAM and reducing attack surface. From SSH, run:

```bash
cd TheGhettoMCServer
docker compose ps
docker compose logs --tail=100 minecraft
docker compose exec -T minecraft rcon-cli list
docker compose exec -T minecraft rcon-cli "say Hello from my iPhone"
docker compose restart minecraft
bash scripts/backup.sh
```

For a Zig CLI, install a compatible Zig release on the Pi, run `cd zig && zig build -Doptimize=ReleaseSmall`; run `./zig-out/bin/mcctl status` **from the repository root**. Zig version compatibility must be verified against the installed compiler.

## F. Optimization and stability

- `MC_MEMORY=1152M` in `.env`; don't allocate all 2 GB to Java. `mem_limit: 1600m` leaves space for Linux, networking and page cache. If the container is OOM-killed, reduce heap to 1024M and inspect logs.
- View distance 5, simulation distance 4, max players 3. Avoid massive farms, lots of mobs, and simultaneous exploration.
- Paper is preferred over vanilla for optimizations. Avoid additional plugins, Dynmap, a web control panel, desktop GUI or graphical Waveshare drivers on this Pi.
- Consider pregenerating a **small** world on a more powerful computer and transferring it to the Pi. Generating many chunks on the Pi itself can cause severe lag and fill the SD card.
- Keep the Pi cool, use Ethernet and a quality power supply. Check throttling with `vcgencmd get_throttled`, memory with `free -h`, disk with `df -h`, and server tick time with `docker compose exec -T minecraft rcon-cli tps` (where supported).
- Stop the server cleanly before unplugging the Pi. The included backup script stops the server for a consistent archive; periodically copy backups off-device.

## G. Maintenance, updates and security

```bash
bash scripts/backup.sh
git pull
docker compose pull
docker compose up -d
```

Pin Minecraft versions after confirming compatibility; don't blindly update Paper/Geyser. Java online authentication stays enabled. Configure a whitelist once everyone has joined. Never commit `.env`, `data/`, Floodgate keys or world saves. SSH/Tailscale admin access is private. Only expose Minecraft gameplay ports.

## H. Troubleshooting

- **Cannot SSH**: OS not flashed, SSH disabled, wrong username, wrong network, or mDNS unavailable. Find LAN IP in router.
- **Java can join but Bedrock cannot**: verify Geyser plugin logs, Floodgate auth, correct Bedrock client version, TCP+UDP 19132 forwarding, and NetherNet transport.
- **Server OOM / exit 137**: lower heap, remove extra plugins, inspect `docker compose logs minecraft`.
- **TPS low**: reduce view/simulation distance, avoid exploration while others play, check CPU temperature and SD card health.
- **Friends cannot connect remotely**: check CGNAT, router rules, public address and firewall; test locally first.

References: [Geyser](https://geysermc.org/wiki/geyser/setup/) · [Floodgate](https://geysermc.org/wiki/floodgate/setup/) · [Docker Minecraft](https://docker-minecraft-server.readthedocs.io/) · [Raspberry Pi Imager](https://www.raspberrypi.com/software/).

## Public address: mc.kiem.net

The server currently advertises **TheGhettoMCServer** in its MOTD. **mc.kiem.net is only a future option** if you purchase or control that domain. This **does not create DNS or expose your Pi to the internet**. To make the hostname resolve after your Pi is installed:

1. You must own or control the DNS zone `kiem.net`. At your DNS provider, create an **A record** with name `mc` pointing to your home public IPv4 address. If the address changes, set up dynamic DNS updates. Do not publish a fake AAAA record if you have no working IPv6 route.
2. Reserve a stable local IP for the Pi in your router. Forward **TCP 25565** for Java and **TCP+UDP 19132** for Bedrock to that local IP. Do not forward SSH (22), RCON (25575), or Tailscale administration.
3. Test local joins first, then have a friend test from a different internet connection. If your ISP uses CGNAT, ordinary port forwarding will not work; use a compatible public TCP+UDP tunnel or hosting provider.
4. Java players enter `mc.kiem.net` (default 25565). Bedrock players enter `mc.kiem.net` and port **19132**. An SRV record is optional and cannot replace a missing A/AAAA record.

**DNS is not configured by this repository.** Domain ownership and DNS-provider access are required before it can be made live.

## Three-player performance and stress-test checklist

This configuration targets **three concurrent players**, Paper Java **26.3**, Geyser/Floodgate, 1152 MB heap, view distance 5, simulation distance 4, and a maximum of three players. These are conservative defaults, **not guaranteed smooth performance** on a 2 GB Pi 4. Rendering distance and FPS on each device are client-side settings; use 4–6 chunks and low graphics on weaker devices.

Before inviting friends, run `python3 scripts/check_config.py`, `python3 -m unittest discover -s tests -v`, `bash -n scripts/*.sh`, and `docker compose config --quiet` on a Docker host. These validate configuration, not real multiplayer behavior.

Once the Pi is running, use `bash scripts/healthcheck.sh` to capture memory, temperature, throttling, TPS, logs, and listening ports. For a real three-player load test:

1. Back up the world, join as one Java player, one iPad Bedrock player, and one Windows Bedrock player.
2. Play together for 10 minutes while stationary, then explore separately for 10 minutes to trigger chunk generation.
3. Run `bash scripts/healthcheck.sh` before, during and after. Check sustained TPS near 20, lack of out-of-memory errors, acceptable device FPS and no disconnects. Record whether Bedrock NetherNet joins work from both LAN and internet.
4. If exploration causes lag, pre-generate a limited world on a stronger machine and copy it to the Pi. Avoid heavy plugins and large mob farms. If the Pi cannot sustain three players, move hosting to a more capable device.

**Do not run aggressive synthetic traffic floods or large chunk-generation stress tests on the 2 GB Pi.** The tests in GitHub Actions are static/unit tests, not a substitute for a real Paper+Geyser multiplayer test.


## Operational hardening and recovery

- The Docker container has all Linux capabilities dropped, no-new-privileges, a PID cap, and bounded Docker logs. These measures reduce risk but do not guarantee isolation from vulnerabilities in the container runtime, plugins or host kernel.
- RCON is used only **inside the Minecraft container** by `docker compose exec`; it has no published host port. Never publish TCP 25575 or put an RCON dashboard on the public internet.
- The backup script stops Minecraft, creates a temporary archive, validates that the archive is readable, atomically renames it, and restarts the server even if archiving fails. A readable archive is not proof that the world restores successfully: periodically restore a copy on another machine.
- Use a strong unique SSH password or SSH keys, disable password login after key-based SSH is verified, keep Raspberry Pi OS and Docker updated, and administer over Tailscale. Don't expose SSH on your router.
- To avoid downtime after power loss, Docker's `restart: unless-stopped` will restart the server when Docker returns, but it cannot protect against SD corruption, network failure, a broken plugin, or loss of electricity. Use a UPS for better uptime.
- For **free off-site backups**, configure a personal cloud storage account with [rclone](https://rclone.org/) on the Pi. Use `rclone crypt` for client-side encryption and an independently stored recovery password. Never commit cloud credentials or encryption passwords. Free storage quotas and upload reliability vary; this is optional and not yet configured.
- A CDN does not improve Minecraft game-state traffic or preserve your world. A TCP/UDP tunnel can provide a convenient public address, but the tunnel provider and home internet remain additional availability dependencies.
- For a genuinely resilient setup, monitor disk space, Pi throttling, memory, TPS, backup age, and periodically rehearse restoration.
