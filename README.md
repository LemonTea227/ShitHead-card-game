# ShitHead Card Game

Legacy client/server card game project modernized for Python 3.

## Requirements

- Python 3.10+
- `pip install .`
- `pip install ".[dev]"`

## Run

Open two terminals from the project root.

1. Start server:

```powershell
cd "ShitHead Server"
python project_server.py
```

2. Start client:

```powershell
cd "ShitHead Client"
python project_client.py
```

## LAN / Remote Play

By default, the server binds to `127.0.0.1` (localhost) for safety.

### LAN play (friends on same network)

1. Run server in LAN mode on the host machine:

```powershell
cd "ShitHead Server"
python project_server.py --lan --port 22073
```

2. Find your host machine LAN IP (for example `192.168.1.50`).

3. Each client connects with:

```powershell
cd "ShitHead Client"
python project_client.py --host 192.168.1.50 --port 22073
```

### Safer free remote play (recommended): Tailscale

For internet play without exposing ports publicly, use Tailscale (free tier).

1. Install Tailscale on host + all clients and join the same tailnet.
2. On host, run:

```powershell
cd "ShitHead Server"
python project_server.py --host <HOST_TAILSCALE_IP> --port 22073
```

3. Friends run client with the same Tailscale host IP:

```powershell
cd "ShitHead Client"
python project_client.py --host <HOST_TAILSCALE_IP> --port 22073
```

### Security notes

- Avoid exposing the server directly to the public internet via port forwarding.
- If you use `--lan` (`0.0.0.0`), allow access only from trusted networks/devices.
- You can also set `SHITHEAD_SERVER_HOST` and `SHITHEAD_SERVER_PORT` environment variables instead of CLI flags.

## Formatting

Format all Python files from the project root:

```powershell
python -m black .
```

## Linting

Run the linter from the project root:

```powershell
python -m ruff check .
```

Optional autofix for safe fixes:

```powershell
python -m ruff check . --fix
```

## Notes

- The protocol uses shared size-prefixed TCP framing in `common/net_protocol.py`.
- Client assets are loaded from `ShitHead Client/proj_pics`.
- Client preferences are stored in `ShitHead Client/preferences.json`.
