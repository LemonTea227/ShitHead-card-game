# ShitHead Card Game

Legacy client/server card game project modernized for Python 3.

## Requirements

- Python 3.10+
- `pip install .`
- `pip install .[dev]`

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
