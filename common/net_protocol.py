from __future__ import annotations

import logging
import socket
import struct
from typing import Union

logger = logging.getLogger("shithead.protocol")

SIZE_HEADER_FORMAT = "00000|"
SIZE_HEADER_SIZE = len(SIZE_HEADER_FORMAT)
TCP_DEBUG = False

TextOrBytes = Union[str, bytes, bytearray]


def to_bytes(data: TextOrBytes) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, bytearray):
        return bytes(data)
    return str(data).encode("utf-8")


def to_text(data: TextOrBytes) -> str:
    if isinstance(data, str):
        return data
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise socket.error("Failed to decode payload as UTF-8") from exc


def recv_by_size(sock: socket.socket) -> str:
    header = b""
    while len(header) < SIZE_HEADER_SIZE:
        chunk = sock.recv(SIZE_HEADER_SIZE - len(header))
        if not chunk:
            return ""
        header += chunk

    if header[-1:] != b"|":
        logger.debug("recv_by_size: missing '|' delimiter in header")
        return ""
    try:
        size_str = header[: SIZE_HEADER_SIZE - 1].decode("ascii")
        if not size_str.isdigit():
            return ""
        data_len = int(size_str)
    except (UnicodeDecodeError, ValueError):
        return ""
    data = bytearray()
    while len(data) < data_len:
        chunk = sock.recv(data_len - len(data))
        if not chunk:
            return ""
        data.extend(chunk)

    if data_len != len(data):
        return ""

    text_data = to_text(data)
    if TCP_DEBUG and text_data:
        preview = text_data if len(text_data) <= 100 else text_data[:100]
        logger.debug("Recv(%s)>>>%s", to_text(header), preview)
    return text_data


def send_with_size(sock: socket.socket, data: TextOrBytes) -> None:
    payload = to_bytes(data)
    if not payload:
        raise socket.error("Cannot send empty payload")
    # Maximum value that fits in SIZE_HEADER_SIZE-1 decimal digits
    max_payload = 10 ** (SIZE_HEADER_SIZE - 1) - 1
    if len(payload) > max_payload:
        raise socket.error(
            f"Payload too large: {len(payload)} bytes exceeds max {max_payload}"
        )
    header = str(len(payload)).zfill(SIZE_HEADER_SIZE - 1) + "|"
    packet = header.encode("ascii") + payload
    sock.sendall(packet)

    if TCP_DEBUG and payload:
        text_payload = to_text(payload)
        preview = (
            text_payload if len(text_payload) <= 100 else text_payload[:100]
        )
        logger.debug("Sent(%s)>>>%s", len(payload), preview)


def send_one_message(sock: socket.socket, data: TextOrBytes) -> None:
    payload = to_bytes(data)
    length = socket.htonl(len(payload))
    sock.sendall(struct.pack("I", length) + payload)

    if TCP_DEBUG and payload:
        text_payload = to_text(payload)
        preview = (
            text_payload if len(text_payload) <= 100 else text_payload[:100]
        )
        logger.debug("Sent(%s)>>>%s", len(payload), preview)


def recv_one_message(sock: socket.socket) -> str:
    len_section = _recv_amount(sock, 4)
    if not len_section:
        return ""

    (len_int,) = struct.unpack("I", len_section)
    len_int = socket.ntohl(len_int)
    data = _recv_amount(sock, len_int)
    if data is None or len_int != len(data):
        return ""

    text_data = to_text(data)
    if TCP_DEBUG and text_data:
        preview = text_data if len(text_data) <= 100 else text_data[:100]
        logger.debug("Recv(%s)>>>%s", len_int, preview)
    return text_data


def _recv_amount(sock: socket.socket, size: int) -> bytes | None:
    buffer = bytearray()
    remaining = size
    while remaining:
        new_buffer = sock.recv(remaining)
        if not new_buffer:
            return None
        buffer.extend(new_buffer)
        remaining -= len(new_buffer)
    return bytes(buffer)
