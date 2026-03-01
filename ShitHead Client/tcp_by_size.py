import os
import socket
import sys

try:
    from common.net_protocol import recv_by_size
    from common.net_protocol import recv_one_message
    from common.net_protocol import send_one_message
    from common.net_protocol import send_with_size
except ModuleNotFoundError:
    REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    from common.net_protocol import recv_by_size
    from common.net_protocol import recv_one_message
    from common.net_protocol import send_one_message
    from common.net_protocol import send_with_size


def main_for_test(role: str) -> None:
    import time

    port = 12312
    if role == "srv":
        s = socket.socket()
        s.bind(("0.0.0.0", port))
        s.listen(1)
        cli_s, _ = s.accept()
        data = recv_by_size(cli_s)
        print("1 server got:" + data)
        send_with_size(cli_s, "1 back:" + data)
        time.sleep(3)

        print("\n\n\nServer Binary Section\n")
        data = recv_one_message(cli_s)
        print("2 server got:" + data)
        send_one_message(cli_s, "2 back:" + data)

        cli_s.close()
        time.sleep(3)
        s.close()
    elif role == "cli":
        c = socket.socket()
        c.connect(("127.0.0.1", port))
        send_with_size(c, "ABC")

        print("1 client got:" + recv_by_size(c))
        time.sleep(3)

        print("\n\n\nClient Binary Section\n")
        send_one_message(c, "abcdefghijklmnop")

        print("2 client got:" + recv_one_message(c))
        time.sleep(3)
        c.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2:
        main_for_test(sys.argv[1])
