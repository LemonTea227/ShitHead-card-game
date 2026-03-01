# ShitHead Card Game

Legacy client/server card game project modernized for Python 3.

## Requirements

- Python 3.10+
- `pip install -r requirements.txt`
- `pip install -r requirements-dev.txt`

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

## Notes

- The protocol uses custom size-prefixed TCP framing implemented in both `tcp_by_size.py` files.
- Client assets are loaded from `ShitHead Client/proj_pics`.
