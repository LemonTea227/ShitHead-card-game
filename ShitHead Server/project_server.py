import socket
import threading
import time
import logging
import argparse
import os
from typing import List, Optional, Tuple

import game
from tcp_by_size import send_with_size, recv_by_size

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 22073
IP = DEFAULT_HOST
PORT = DEFAULT_PORT
SEND: dict[socket.socket, list[str]] = {}
THREAD: list[threading.Thread] = []
ONLINE_GAMES: list[game.Game] = []
QUICK_GAMES: list[game.Game] = []
AVAILABLE_GAMES: list[game.Game] = []

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("shithead.server")


def _parse_host_port() -> tuple[str, int]:
    parser = argparse.ArgumentParser(
        description="Run ShitHead server with configurable bind host/port"
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("SHITHEAD_SERVER_HOST", DEFAULT_HOST),
        help=(
            "Host/interface to bind. Defaults to 127.0.0.1 for safety. "
            "Use 0.0.0.0 or --lan for LAN access."
        ),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("SHITHEAD_SERVER_PORT", DEFAULT_PORT)),
        help="Port to bind (default: 22073)",
    )
    parser.add_argument(
        "--lan",
        action="store_true",
        help="Convenience flag: bind to 0.0.0.0 for LAN clients",
    )
    args = parser.parse_args()

    host = "0.0.0.0" if args.lan else str(args.host).strip()
    port = int(args.port)

    if not host:
        raise ValueError("host must not be empty")
    if not (1 <= port <= 65535):
        raise ValueError("port must be in range 1..65535")
    return host, port


def main() -> None:
    global IP, PORT
    IP, PORT = _parse_host_port()

    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen(5)

    logger.info("server listening on %s:%s", IP, PORT)
    if IP == "0.0.0.0":
        logger.warning(
            "LAN/public bind enabled. Only use with trusted clients and "
            "firewall rules."
        )

    while True:
        # open socket with client
        client_socket, address = server_socket.accept()
        logger.info("connected socket=%s address=%s", client_socket, address)
        client_socket.settimeout(0.1)
        SEND[client_socket] = []
        t = threading.Thread(target=async_send_receive, args=(client_socket,))
        t.start()
        THREAD.append(t)

    server_socket.close()
    for t in THREAD:
        t.join()


def quick_game(sock: socket.socket, preferences: int) -> None:
    """
    this function is responsible for finding a quick game
    :param sock:
    :param preferences:
    :return: None
    """
    the_game = None
    for room in QUICK_GAMES:
        if (
            room.max_players == preferences
            and len(room.players) != room.max_players
        ):
            the_game = room

    if not the_game:
        create_a_room(sock, preferences)
    else:
        if not join_game(sock, the_game):
            logger.debug("retry quick_game for sock=%s", sock)
            quick_game(sock, preferences)


def _send_waiting_update(room: game.Game) -> None:
    for player in room.players:
        SEND[player].append(
            "UPDATE"
            + "~"
            + str(room.num_room)
            + ","
            + str(len(room.players))
            + ","
            + str(room.max_players)
            + "~~~"
        )


def _cleanup_room_lists(room: game.Game) -> None:
    should_remove = room.finished or len(room.players) == 0
    if not should_remove:
        return
    if room in ONLINE_GAMES:
        ONLINE_GAMES.remove(room)
    if room in QUICK_GAMES:
        QUICK_GAMES.remove(room)
    if room in AVAILABLE_GAMES:
        AVAILABLE_GAMES.remove(room)


def choose_a_room(sock: socket.socket) -> None:
    """
    this function is responsible for sending all the games to the client
    :param sock:
    :return:
    """
    message = "GAMES~"
    for room in AVAILABLE_GAMES:
        message += (
            str(room.num_room)
            + ","
            + str(len(room.players))
            + ","
            + str(room.max_players)
            + "~"
        )
    for room in QUICK_GAMES:
        message += (
            str(room.num_room)
            + ","
            + str(len(room.players))
            + ","
            + str(room.max_players)
            + "~"
        )
    for room in ONLINE_GAMES:
        message += (
            str(room.num_room)
            + ","
            + str(len(room.players))
            + ","
            + str(room.max_players)
            + "~"
        )
    message += "~~"
    SEND[sock].append(message)


def create_a_private_room(sock: socket.socket, num_players: int) -> None:
    """
    this function is responsible for creating a private room
    :param sock:
    :param num_players:
    :return:
    """
    room = game.Game(
        len(QUICK_GAMES) + len(ONLINE_GAMES) + len(AVAILABLE_GAMES),
        num_players,
        [],
    )
    AVAILABLE_GAMES.append(room)
    logger.info(
        "created private room=%s max_players=%s",
        room.num_room,
        room.max_players,
    )
    join_private_game(sock, room)


def create_a_room(sock: socket.socket, num_players: int) -> None:
    """
    this function is responsible for creating a room
    :param sock:
    :param num_players:
    :return:
    """
    room = game.Game(
        len(QUICK_GAMES) + len(ONLINE_GAMES) + len(AVAILABLE_GAMES),
        num_players,
        [],
    )
    QUICK_GAMES.append(room)
    logger.info(
        "created room=%s max_players=%s", room.num_room, room.max_players
    )
    join_game(sock, room)
    logger.info(
        "room status room=%s max=%s players=%s",
        room.num_room,
        room.max_players,
        len(room.players),
    )


def join_private_game(sock: socket.socket, room: game.Game) -> bool:
    """
    this function is responsible for joining a private room
    :param sock:
    :param room:
    :return: if joined: True, if not joined: False.
    """
    # print 'num_room: ' + str(room.num_room)

    if room and room.max_players == len(room.players):
        AVAILABLE_GAMES.remove(room)
        ONLINE_GAMES.append(room)
        return False
    if room and sock not in room.players:
        room.add_player(sock)
    _send_waiting_update(room)

    if room.max_players == len(room.players) and not room.started:
        room.start_game()
    cancelled_waiting = False
    while not room.finished and not cancelled_waiting:
        try:
            if SEND[sock]:
                send_with_size(sock, SEND[sock].pop(0))
            if sock in room.send_dict:
                if room.send_dict[sock]:
                    message = room.send_dict[sock].pop(0)
                    send_with_size(sock, message)
                    if "GAME~FINISH~" in message:
                        room.finished = True
            if not room.max_players == len(room.players):
                time.sleep(1)
            data = recv_by_size(sock)
            if not data:
                raise socket.error
            message = _parse_message(data)
            if (
                not room.started
                and message
                and message[0].upper() == "WAITING"
                and len(message) > 1
                and message[1].upper() == "CANCEL"
            ):
                del_player_from_waiting(sock)
                cancelled_waiting = True
                continue
            receive_handler_thread = threading.Thread(
                target=receive_game_handler,
                args=(
                    sock,
                    data,
                    room,
                ),
            )
            receive_handler_thread.start()
            THREAD.append(receive_handler_thread)

        except socket.timeout:
            continue

        except socket.error:
            room.remove_player(sock)
            if not room.started:
                del_player_from_waiting(sock)

    _cleanup_room_lists(room)

    return True


def join_game(sock: socket.socket, room: game.Game) -> bool:
    """
    this function is responsible for joining a room (game)
    :param sock:
    :param room:
    :return: if joined: True, if not joined: False.
    """
    # print 'num_room: ' + str(room.num_room)

    if room.max_players == len(room.players):
        QUICK_GAMES.remove(room)
        ONLINE_GAMES.append(room)
        return False
    if sock not in room.players:
        room.add_player(sock)
    _send_waiting_update(room)

    if room.max_players == len(room.players) and not room.started:
        room.start_game()
    finished = False
    cancelled_waiting = False
    while not finished and not cancelled_waiting:
        try:
            if SEND[sock]:
                send_with_size(sock, SEND[sock].pop(0))
            if sock in room.send_dict:
                if room.send_dict[sock]:
                    message = room.send_dict[sock].pop(0)
                    send_with_size(sock, message)
                    if "GAME~FINISH~" in message:
                        finished = True
            if not room.max_players == len(room.players):
                time.sleep(1)
            data = recv_by_size(sock)
            if not data:
                raise socket.error
            message = _parse_message(data)
            if (
                not room.started
                and message
                and message[0].upper() == "WAITING"
                and len(message) > 1
                and message[1].upper() == "CANCEL"
            ):
                del_player_from_waiting(sock)
                cancelled_waiting = True
                continue
            receive_handler_thread = threading.Thread(
                target=receive_game_handler,
                args=(
                    sock,
                    data,
                    room,
                ),
            )
            receive_handler_thread.start()
            THREAD.append(receive_handler_thread)

        except socket.timeout:
            continue

        except socket.error:
            room.remove_player(sock)
            if not room.started:
                del_player_from_waiting(sock)

    _cleanup_room_lists(room)

    return True


def _parse_card(card: str) -> Optional[Tuple[int, int]]:
    parts = card.split(",")
    if len(parts) != 2:
        return None
    num_card = _safe_int(parts[0])
    shape_card = _safe_int(parts[1])
    if num_card is None or shape_card is None:
        return None
    return num_card, shape_card


def _parse_cards(cards: str) -> List[Tuple[int, int]]:
    parsed_cards: List[Tuple[int, int]] = []
    for raw_card in cards.split("|"):
        if not raw_card:
            continue
        card = _parse_card(raw_card)
        if card is not None:
            parsed_cards.append(card)
    return parsed_cards


def receive_game_handler(
    sock: socket.socket, receive: str, room: game.Game
) -> None:
    """
    this function is responsible for handling game receives
    :param sock:
    :param receive:
    :param room:
    :return: None
    """
    message = _parse_message(receive)
    if not message:
        return
    if message[0].upper() == "GAME" and len(message) > 2:
        action = message[1].upper()
        if action == "THROW":
            if len(message[2]) > 1:
                card_lst = _parse_cards(message[2])
                to_who = 0
                if len(message) > 3 and message[3] != "":
                    parsed_to_who = _safe_int(message[3])
                    to_who = parsed_to_who if parsed_to_who is not None else 0
                room.throw(sock, card_lst, to_who)
            else:
                to_who = 0
                if message[2] != "":
                    parsed_to_who = _safe_int(message[2])
                    to_who = parsed_to_who if parsed_to_who is not None else 0
                room.throw(sock, [], to_who)
        elif action == "TAKE_DECK_TO_HAND":
            room.take_deck(sock)


def find_room_by_num_room(num_room: int) -> Optional[game.Game]:
    """
    this function is responsible for finding a room by the number of the room
    :param num_room:
    :return:
    """
    for room in QUICK_GAMES:
        if room.num_room == num_room:
            return room

    for room in AVAILABLE_GAMES:
        if room.num_room == num_room:
            return room

    logger.debug("room not found for room_num=%s", num_room)
    return None


def del_player_from_waiting(sock: socket.socket) -> bool:
    """
    this function is responsible for deleting a player from a room and if the
    room gets empty also the room
    :param sock:
    :return:
    """
    found = False
    for room in QUICK_GAMES:
        if sock in room.players:
            room.players.remove(sock)
            if len(room.players) == 0:
                QUICK_GAMES.remove(room)
            else:
                _send_waiting_update(room)
            found = True
            break

    if not found:
        for room in AVAILABLE_GAMES:
            if sock in room.players:
                room.players.remove(sock)
                if len(room.players) == 0:
                    AVAILABLE_GAMES.remove(room)
                else:
                    _send_waiting_update(room)
                found = True
                break

    return found


def async_send_receive(sock: socket.socket) -> None:
    """
    this function is responsible for the sending and receiving with the client
    :param sock: the client's socket :type socket._socketobject
    :return: None
    """
    while True:
        try:
            try:
                if SEND[sock]:
                    send_with_size(sock, SEND[sock].pop(0))
                data = recv_by_size(sock)
                if not data:
                    raise socket.error
                receive_handler(sock, data)

            except socket.timeout:
                continue
        except socket.error:
            logger.info("disconnecting player sock=%s", sock)
            del_player_from_waiting(sock)
            SEND.pop(sock, None)
            break


def _parse_message(recv: str) -> List[str]:
    stripped = recv[:-2]
    return stripped.split("~")


def _safe_int(value: str) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def handle_client_request(sock: socket.socket, message: List[str]) -> None:
    if not message:
        return

    command = message[0].upper()
    if command == "QUICK_GAME" and len(message) == 3:
        max_players = _safe_int(message[1])
        if max_players is None:
            logger.warning("invalid QUICK_GAME payload: %s", message)
            return
        quick_game(sock, max_players)
        return

    if command == "SCREEN" and len(message) > 2:
        action = message[1].upper()
        if action == "CHOOSE_A_ROOM":
            choose_a_room(sock)
            return
        if action == "CREATE_A_ROOM":
            players = _safe_int(message[2])
            if players is None:
                logger.warning("invalid CREATE_A_ROOM payload: %s", message)
                return
            create_a_private_room(sock, players)
            return

    if command == "JOIN" and len(message) > 2:
        room_num = _safe_int(message[1])
        if room_num is None:
            logger.warning("invalid JOIN payload: %s", message)
            return

        room = find_room_by_num_room(room_num)
        if room in QUICK_GAMES:
            join_game(sock, room)
        elif room in AVAILABLE_GAMES:
            join_private_game(sock, room)
        return

    logger.debug("unhandled client message: %s", message)


def receive_handler(sock: socket.socket, recv: str) -> None:
    """
    this function is responsible for handeling with the received messages and
    adding messages to the SEND by the
    protocol.
    :param  :type
    :return:
    """
    message = _parse_message(recv)
    handle_client_request(sock, message)


if __name__ == "__main__":
    main()
