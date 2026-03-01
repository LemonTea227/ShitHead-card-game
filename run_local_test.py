import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERVER_DIR = ROOT / "ShitHead Server"
CLIENT_DIR = ROOT / "ShitHead Client"


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


def main():
    python_executable = sys.executable
    server = None
    client_one = None
    client_two = None

    try:
        server = start_process([python_executable, "project_server.py"], SERVER_DIR)
        time.sleep(1.0)

        client_one = start_process([python_executable, "project_client.py"], CLIENT_DIR)
        time.sleep(0.5)
        client_two = start_process([python_executable, "project_client.py"], CLIENT_DIR)

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
