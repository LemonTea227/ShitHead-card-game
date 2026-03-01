import socket
import struct

SIZE_HEADER_FORMAT = "00000|"  # n digits for data size + one delimiter
size_header_size = len(SIZE_HEADER_FORMAT)
TCP_DEBUG = False


def _to_bytes(data):
    if isinstance(data, bytes):
        return data
    return str(data).encode("utf-8")


def _to_text(data):
    if isinstance(data, str):
        return data
    return data.decode("utf-8")


def recv_by_size(sock):
    header = b""
    while len(header) < size_header_size:
        chunk = sock.recv(size_header_size - len(header))
        if not chunk:
            return ""
        header += chunk

    data_len = int(header[: size_header_size - 1].decode("ascii"))
    data = b""
    while len(data) < data_len:
        chunk = sock.recv(data_len - len(data))
        if not chunk:
            return ""
        data += chunk

    if data_len != len(data):
        return ""

    text_data = _to_text(data)
    if TCP_DEBUG and text_data:
        preview = text_data if len(text_data) <= 100 else text_data[:100]
        print("\nRecv({})>>>{}".format(_to_text(header), preview))
    return text_data


def send_with_size(sock, data):
    payload = _to_bytes(data)
    header = str(len(payload)).zfill(size_header_size - 1) + "|"
    packet = header.encode("ascii") + payload
    sock.sendall(packet)
    if TCP_DEBUG and payload:
        text_payload = _to_text(payload)
        preview = (
            text_payload if len(text_payload) <= 100 else text_payload[:100]
        )
        print("\nSent({})>>>{}".format(len(payload), preview))


def send_one_message(sock, data):
    payload = _to_bytes(data)
    length = socket.htonl(len(payload))
    sock.sendall(struct.pack("I", length) + payload)
    if TCP_DEBUG and payload:
        text_payload = _to_text(payload)
        preview = (
            text_payload if len(text_payload) <= 100 else text_payload[:100]
        )
        print("\nSent({})>>>{}".format(len(payload), preview))


def recv_one_message(sock):
    len_section = __recv_amount(sock, 4)
    if not len_section:
        return None

    (len_int,) = struct.unpack("I", len_section)
    len_int = socket.ntohl(len_int)
    data = __recv_amount(sock, len_int)
    if data is None or len_int != len(data):
        return ""

    text_data = _to_text(data)
    if TCP_DEBUG and text_data:
        preview = text_data if len(text_data) <= 100 else text_data[:100]
        print("\nRecv({})>>>{}".format(len_int, preview))
    return text_data


def __recv_amount(sock, size):
    buffer = b""
    while size:
        new_buffer = sock.recv(size)
        if not new_buffer:
            return None
        buffer += new_buffer
        size -= len(new_buffer)
    return buffer


def main_for_test(role):
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
