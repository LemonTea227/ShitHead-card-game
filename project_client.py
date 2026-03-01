import os
import runpy
import sys
from pathlib import Path


def resolve_python_executable(root: Path) -> str:
    candidates = [
        root / ".venv" / "Scripts" / "python.exe",
        root / ".venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable


def main() -> None:
    root = Path(__file__).resolve().parent
    client_dir = root / "ShitHead Client"
    client_entry = client_dir / "project_client.py"

    if not client_entry.exists():
        raise FileNotFoundError(
            "Could not find ShitHead Client/project_client.py"
        )

    target_python = resolve_python_executable(root)
    os.chdir(str(client_dir))
    client_dir_str = str(client_dir)
    if client_dir_str not in sys.path:
        sys.path.insert(0, client_dir_str)
    if Path(sys.executable).resolve() != Path(target_python).resolve():
        os.execv(
            target_python, [target_python, str(client_entry), *sys.argv[1:]]
        )
    runpy.run_path(str(client_entry), run_name="__main__")


if __name__ == "__main__":
    main()
