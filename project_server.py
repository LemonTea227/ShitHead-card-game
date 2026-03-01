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
    server_dir = root / "ShitHead Server"
    server_entry = server_dir / "project_server.py"

    if not server_entry.exists():
        raise FileNotFoundError(
            "Could not find ShitHead Server/project_server.py"
        )

    target_python = resolve_python_executable(root)
    if Path(sys.executable).resolve() != Path(target_python).resolve():
        os.execv(
            target_python, [target_python, str(server_entry), *sys.argv[1:]]
        )

    os.chdir(str(server_dir))
    runpy.run_path(str(server_entry), run_name="__main__")


if __name__ == "__main__":
    main()
