import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERVER_DIR = ROOT / "ShitHead Server"
CLIENT_DIR = ROOT / "ShitHead Client"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 22073


def resolve_python_executable():
    windows_venv_python = ROOT / ".venv" / "Scripts" / "python.exe"
    unix_venv_python = ROOT / ".venv" / "bin" / "python"

    if windows_venv_python.exists():
        return str(windows_venv_python)
    if unix_venv_python.exists():
        return str(unix_venv_python)
    return sys.executable


def start_process(command, cwd):
    return subprocess.Popen(command, cwd=str(cwd))


def terminate_process(process):
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def is_port_in_use(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def main():
    python_executable = resolve_python_executable()
    server = None
    client_one = None
    client_two = None

    if is_port_in_use(SERVER_HOST, SERVER_PORT):
        print(
            "Port {} is already in use. Stop the existing server first."
            .format(
                SERVER_PORT
            )
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

        client_one = start_process(
            [python_executable, "project_client.py"],
            CLIENT_DIR,
        )
        time.sleep(0.5)
        client_two = start_process(
            [python_executable, "project_client.py"],
            CLIENT_DIR,
        )

        print("Started server and two clients. Press Ctrl+C to stop all.")

        while True:
            if server.poll() is not None:
                print("Server exited. Stopping clients.")
                break
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Stopping all processes...")
    finally:
        terminate_process(client_two)
        terminate_process(client_one)
        terminate_process(server)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.default_int_handler)
    main()
