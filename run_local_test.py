import json
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parent
SERVER_DIR = ROOT / "ShitHead Server"
CLIENT_DIR = ROOT / "ShitHead Client"
PREFERENCES_PATH = CLIENT_DIR / "preferences.json"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 22073


def resolve_python_executable() -> str:
    windows_venv_python = ROOT / ".venv" / "Scripts" / "python.exe"
    unix_venv_python = ROOT / ".venv" / "bin" / "python"

    if windows_venv_python.exists():
        return str(windows_venv_python)
    if unix_venv_python.exists():
        return str(unix_venv_python)
    return sys.executable


def start_process(command: Sequence[str], cwd: Path) -> subprocess.Popen:
    return subprocess.Popen(command, cwd=str(cwd))


def terminate_process(process: subprocess.Popen | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass


def is_port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def read_preferences_count(default: int = 2) -> int:
    try:
        with open(PREFERENCES_PATH, "r", encoding="utf-8") as pref_file:
            data = json.load(pref_file)
            value = int(data.get("quick_game_players", default))
            return max(2, min(4, value))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return default


def main() -> None:
    python_executable = resolve_python_executable()
    server = None
    clients = []

    if is_port_in_use(SERVER_HOST, SERVER_PORT):
        print(
            "Port {} is already in use. "
            "Stop the existing server first.".format(SERVER_PORT)
        )
        return

    try:
        server = start_process(
            [python_executable, "project_server.py"],
            SERVER_DIR,
        )
        time.sleep(1.0)

        if server.poll() is not None:
            print("Server failed to start. Check server logs/output.")
            return

        for _ in range(read_preferences_count()):
            clients.append(start_process(
                [python_executable, "project_client.py"],
                CLIENT_DIR,
            ))
            time.sleep(0.5)

        print(
            f"Started server and {len(clients)} client(s). "
            "Press Ctrl+C to stop all."
        )

        while True:
            if server.poll() is not None:
                print("Server exited. Stopping clients.")
                break
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Stopping all processes...")
    finally:
        for client_process in reversed(clients):
            terminate_process(client_process)
        terminate_process(server)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.default_int_handler)
    main()
