import os
import json
import socket
import sys
import threading
import argparse
from collections import deque
from pathlib import Path
from typing import Optional, Sequence, TypeAlias

try:
    import pygame
except ModuleNotFoundError as import_error:
    if (
        import_error.name == "pygame"
        and os.environ.get("SHITHEAD_VENV_BOOTSTRAPPED") != "1"
    ):
        root = Path(__file__).resolve().parents[1]
        candidates = [
            root / ".venv" / "Scripts" / "python.exe",
            root / ".venv" / "bin" / "python",
        ]
        for candidate in candidates:
            if candidate.exists():
                os.environ["SHITHEAD_VENV_BOOTSTRAPPED"] = "1"
                os.execv(
                    str(candidate),
                    [
                        str(candidate),
                        str(Path(__file__).resolve()),
                        *sys.argv[1:],
                    ],
                )
    raise

import button
import cards
from pages import (
    choose_room_page,
    create_room_page,
    finish_page,
    game_page,
    open_page,
    rules_page,
    settings_page,
    waiting_page,
)
from tcp_by_size import send_with_size, recv_by_size

DEFAULT_SERVER_HOST = "127.0.0.1"
DEFAULT_SERVER_PORT = 22073
IP = DEFAULT_SERVER_HOST
PORT = DEFAULT_SERVER_PORT
SEND: deque[str] = deque()
RECEIVE: deque[str] = deque()
THREAD: list[threading.Thread] = []
CLIENT_SOCKET: Optional[socket.socket] = None
SEND_RECEIVE_THREAD: Optional[threading.Thread] = None
CONNECTION_STATUS = "Not connected"
BACKGROUND = "proj_pics/rainbow_background.jpg"  # 1700X956
ICON = "proj_pics/ShitHead_icon_sized.png"  # 250X250
SETTINGS = "proj_pics/settings.png"  # 128X128
MOVE_RIGHT = "proj_pics/move_right.png"  # 220X230
MOVE_LEFT = "proj_pics/move_left.png"  # 220X230
WINDOW_WIDTH = 1700
WINDOW_HEIGHT = 956
BASE_WIDTH = 1700
BASE_HEIGHT = 956
PINK = (255, 20, 147)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (2, 251, 146)
LIGHT_GREY = (200, 200, 200)
LEFT = 1
SCROLL = 2
RIGHT = 3
screen: Optional[pygame.Surface] = None
window_screen: Optional[pygame.Surface] = None
Color: TypeAlias = tuple[int, int, int]
MousePos: TypeAlias = tuple[float, float]
ScreenState: TypeAlias = str | tuple[object, ...]
Colorkey: TypeAlias = Color | None
IMAGE_CACHE: dict[tuple[str, Colorkey], pygame.Surface] = {}
SCALED_IMAGE_CACHE: dict[
    tuple[str, tuple[int, int], Colorkey], pygame.Surface
] = {}
PREFERENCES_JSON = "preferences.json"


def _read_preferences() -> dict[str, object]:
    try:
        with open(PREFERENCES_JSON, "r", encoding="utf-8") as pref_file:
            data = json.load(pref_file)
            if isinstance(data, dict):
                return data
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        pass
    return {}


def _write_preferences(data: dict[str, object]) -> None:
    with open(PREFERENCES_JSON, "w", encoding="utf-8") as pref_file:
        json.dump(data, pref_file, indent=2)


def read_server_preferences(
    default_host: str = DEFAULT_SERVER_HOST,
    default_port: int = DEFAULT_SERVER_PORT,
) -> tuple[str, int]:
    data = _read_preferences()
    host = str(data.get("server_host", default_host)).strip()
    if not host:
        host = default_host

    try:
        port = int(data.get("server_port", default_port))
    except (TypeError, ValueError):
        port = default_port

    if not (1 <= port <= 65535):
        port = default_port

    return host, port


def write_server_preferences(host: str, port: int) -> None:
    clean_host = str(host).strip() or DEFAULT_SERVER_HOST
    clean_port = int(port)
    if not (1 <= clean_port <= 65535):
        raise ValueError("port must be in range 1..65535")

    data = _read_preferences()
    data["server_host"] = clean_host
    data["server_port"] = clean_port
    _write_preferences(data)


def parse_connection_config() -> tuple[str, int]:
    saved_host, saved_port = read_server_preferences()

    parser = argparse.ArgumentParser(
        description="Run ShitHead client and connect to a server"
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Server host/IP to connect to",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Server port to connect to",
    )
    args = parser.parse_args()

    env_host = os.environ.get("SHITHEAD_SERVER_HOST")
    env_port_raw = os.environ.get("SHITHEAD_SERVER_PORT")

    host = args.host if args.host is not None else env_host
    if host is None:
        host = saved_host

    port = args.port
    if port is None and env_port_raw is not None:
        try:
            port = int(env_port_raw)
        except ValueError:
            port = None
    if port is None:
        port = saved_port

    host = str(host).strip()
    port = int(port)
    if not host:
        raise ValueError("host must not be empty")
    if not (1 <= port <= 65535):
        raise ValueError("port must be in range 1..65535")
    return host, port


def load_image(path: str, colorkey: Colorkey = None) -> pygame.Surface:
    key = (path, colorkey)
    image = IMAGE_CACHE.get(key)
    if image is None:
        image = pygame.image.load(path).convert()
        if colorkey is not None:
            image.set_colorkey(colorkey)
        IMAGE_CACHE[key] = image
    return image


def load_scaled_image(
    path: str, size: tuple[int, int], colorkey: Colorkey = None
) -> pygame.Surface:
    key = (path, size, colorkey)
    image = SCALED_IMAGE_CACHE.get(key)
    if image is None:
        image = pygame.transform.smoothscale(load_image(path, colorkey), size)
        SCALED_IMAGE_CACHE[key] = image
    return image


def window_to_virtual(pos: tuple[int, int]) -> tuple[float, float]:
    if window_screen is None:
        return pos

    win_w, win_h = window_screen.get_size()
    if win_w <= 0 or win_h <= 0:
        return pos

    scale_x = float(BASE_WIDTH) / float(win_w)
    scale_y = float(BASE_HEIGHT) / float(win_h)
    return pos[0] * scale_x, pos[1] * scale_y


def render_to_window() -> None:
    if window_screen is None:
        return
    win_w, win_h = window_screen.get_size()
    scaled = pygame.transform.smoothscale(screen, (win_w, win_h))
    window_screen.blit(scaled, (0, 0))
    pygame.display.flip()


def read_preferences_count(default: int = 2) -> int:
    data = _read_preferences()
    try:
        value = int(data.get("quick_game_players", default))
    except (TypeError, ValueError):
        value = default
    return max(2, min(4, value))


def write_preferences_count(num: int) -> None:
    value = max(2, min(4, int(num)))
    data = _read_preferences()
    data["quick_game_players"] = value
    _write_preferences(data)


def is_connected() -> bool:
    return SEND_RECEIVE_THREAD is not None and SEND_RECEIVE_THREAD.is_alive()


def get_connection_status() -> str:
    return CONNECTION_STATUS


def _set_connection_status(message: str) -> None:
    global CONNECTION_STATUS
    CONNECTION_STATUS = message


def connect_to_server(
    host: Optional[str] = None, port: Optional[int] = None
) -> tuple[bool, str]:
    global CLIENT_SOCKET, SEND_RECEIVE_THREAD, IP, PORT

    if is_connected():
        message = f"Connected to {IP}:{PORT}"
        _set_connection_status(message)
        return True, message

    if host is None or port is None:
        pref_host, pref_port = read_server_preferences()
        if host is None:
            host = pref_host
        if port is None:
            port = pref_port

    IP = str(host).strip()
    PORT = int(port)

    if not IP or not (1 <= PORT <= 65535):
        message = "Invalid host or port"
        _set_connection_status(message)
        return False, message

    try:
        sock = socket.socket()
        sock.settimeout(3)
        sock.connect((IP, PORT))
        sock.settimeout(0.1)
        CLIENT_SOCKET = sock
        SEND_RECEIVE_THREAD = threading.Thread(
            target=async_send_receive, args=(sock,)
        )
        SEND_RECEIVE_THREAD.start()
        THREAD.append(SEND_RECEIVE_THREAD)
        message = f"Connected to {IP}:{PORT}"
        _set_connection_status(message)
        return True, message
    except Exception:
        try:
            sock.close()
        except Exception:
            pass
        CLIENT_SOCKET = None
        SEND_RECEIVE_THREAD = None
        message = f"Failed to connect to {IP}:{PORT}"
        _set_connection_status(message)
        return False, message


def disconnect_from_server() -> None:
    global CLIENT_SOCKET, SEND_RECEIVE_THREAD
    if CLIENT_SOCKET is not None:
        try:
            CLIENT_SOCKET.close()
        except Exception:
            pass
    CLIENT_SOCKET = None
    SEND_RECEIVE_THREAD = None


def main() -> None:
    # Init screen
    global IP, PORT
    IP, PORT = parse_connection_config()

    global screen, window_screen
    pygame.init()
    size = (BASE_WIDTH, BASE_HEIGHT)
    window_screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    screen = pygame.Surface(size).convert()
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()

    img = load_image(BACKGROUND)
    screen.blit(img, (0, 0))  # (left, top)
    render_to_window()

    try:
        print(f"Connecting to server {IP}:{PORT}")
        connect_to_server(IP, PORT)

        scrn = "OPEN_SCREEN"
        while True:
            clock.tick(60)
            if SEND_RECEIVE_THREAD is not None and not is_connected():
                disconnect_from_server()
                _set_connection_status("Disconnected from server")
            if RECEIVE:
                scrn = receive_handler(RECEIVE.popleft())
            for event in pygame.event.get():
                pos = window_to_virtual(pygame.mouse.get_pos())
                if event.type == pygame.QUIT:
                    raise RuntimeError("Client closed")
                elif event.type == pygame.VIDEORESIZE:
                    new_size = (max(800, event.w), max(600, event.h))
                    window_screen = pygame.display.set_mode(
                        new_size, pygame.RESIZABLE
                    )
                else:
                    if type(scrn) is not str:
                        scrn = event_handler(scrn[0], pos, event, scrn[1:])
                    else:
                        scrn = event_handler(scrn, pos, event, [])
            render_to_window()
    except Exception as error:
        print(error)

    disconnect_from_server()

    for th in THREAD:
        if th.is_alive():
            th.join()

    pygame.quit()


def open_screen(event: pygame.event.Event, pos: MousePos) -> ScreenState:
    """
    this function is responsible for the opening screen
    :return: what screen to go to (GAME or CREATE or CHOOSE)
    """
    global screen

    img = load_image(BACKGROUND)
    screen.blit(img, (0, 0))  # (left, top)

    quick_game = button.Button(
        WHITE, WINDOW_WIDTH / 2 - 350, 75, 700, 100, "Quick Game"
    )

    settings = load_image(SETTINGS, PINK)
    screen.blit(settings, (WINDOW_WIDTH - 150, 22))

    icon = load_image(ICON, PINK)
    screen.blit(icon, (WINDOW_WIDTH / 2 - 125, 190))
    pygame.display.flip()

    choose_a_room = button.Button(
        WHITE, WINDOW_WIDTH / 2 - 350, 440, 700, 100, "Choose A Room"
    )
    create_a_room = button.Button(
        WHITE, WINDOW_WIDTH / 2 - 350, 590, 700, 100, "Create A Room"
    )
    rules = button.Button(
        WHITE, WINDOW_WIDTH / 2 - 350, 740, 700, 100, "Game Rules"
    )

    next_screen = ""
    red_raw_window(quick_game)
    red_raw_window(choose_a_room)
    red_raw_window(create_a_room)
    red_raw_window(rules)
    pygame.display.update()

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
        if quick_game.is_over(pos):
            next_screen = "QUICK_GAME"

        elif choose_a_room.is_over(pos):
            next_screen = "CHOOSE_A_ROOM"

        elif create_a_room.is_over(pos):
            next_screen = "CREATE_A_ROOM"

        elif rules.is_over(pos):
            next_screen = "RULES"

        elif WINDOW_WIDTH - 150 < pos[0] < WINDOW_WIDTH - 150 + 128:
            if 22 < pos[1] < 22 + 128:
                next_screen = "SETTINGS"
        else:
            next_screen = "OPEN_SCREEN"

    if event.type == pygame.MOUSEMOTION:
        if quick_game.is_over(pos):
            quick_game.color = LIGHT_GREY
        else:
            quick_game.color = WHITE
        if choose_a_room.is_over(pos):
            choose_a_room.color = LIGHT_GREY
        else:
            choose_a_room.color = WHITE
        if create_a_room.is_over(pos):
            create_a_room.color = LIGHT_GREY
        else:
            create_a_room.color = WHITE
        if rules.is_over(pos):
            rules.color = LIGHT_GREY
        else:
            rules.color = WHITE

        pygame.display.flip()

    # print next_screen

    scrn = "OPEN_SCREEN"
    if next_screen == "QUICK_GAME":
        preferences = str(read_preferences_count())
        SEND.append(str(next_screen) + "~" + str(preferences) + "~~~")
    elif next_screen == "CHOOSE_A_ROOM":
        SEND.append("SCREEN~CHOOSE_A_ROOM~~~")
        scrn = "OPEN_SCREEN"
    elif next_screen == "CREATE_A_ROOM":
        num = read_preferences_count()
        scrn = "CREATE_A_ROOM", num
    elif next_screen == "SETTINGS":
        scrn = "SETTINGS"
    elif next_screen == "RULES":
        scrn = "RULES"
    return scrn


def draw_wrapped_lines(
    font: pygame.font.Font,
    lines: list[str],
    x: float,
    y: float,
    max_width: float,
    color: tuple[int, int, int],
) -> float:
    line_space = 4
    line_height = font.get_linesize()
    current_y = y
    for line in lines:
        words = line.split(" ")
        current_line = ""
        for word in words:
            candidate = word if not current_line else current_line + " " + word
            if font.size(candidate)[0] <= max_width:
                current_line = candidate
            else:
                text = font.render(current_line, 1, color)
                screen.blit(text, (x, current_y))
                current_y += line_height + line_space
                current_line = word
        if current_line:
            text = font.render(current_line, 1, color)
            screen.blit(text, (x, current_y))
            current_y += line_height + line_space
    return current_y


def draw_rules_section(
    x: float,
    y: float,
    width: float,
    height: float,
    title: str,
    lines: list[str],
    text_max_width: Optional[float] = None,
) -> None:
    pygame.draw.rect(screen, LIGHT_GREY, (x, y, width, height), 0)
    pygame.draw.rect(screen, BLACK, (x, y, width, height), 3)

    title_font = pygame.font.SysFont("calibri", 38)
    body_font = pygame.font.SysFont("calibri", 25)

    title_text = title_font.render(title, 1, PINK)
    screen.blit(title_text, (x + 15, y + 10))

    if text_max_width is None:
        text_max_width = width - 30

    draw_wrapped_lines(body_font, lines, x + 15, y + 65, text_max_width, BLACK)


def rules_menu(event: pygame.event.Event, pos: MousePos) -> ScreenState:
    global screen

    img = load_image(BACKGROUND)
    screen.blit(img, (0, 0))

    title_font = pygame.font.SysFont("algerian", 64)
    title = title_font.render("ShitHead - Official Rules", 1, WHITE)
    screen.blit(title, (WINDOW_WIDTH / 2 - title.get_width() / 2, 30))

    back_button = load_image(ICON, PINK)
    screen.blit(back_button, (25, 25))

    draw_rules_section(
        60,
        150,
        760,
        220,
        "Setup Game",
        [
            "Each player starts with 3 secret face-down cards, "
            "3 visible face-up cards, and 3 cards in hand.",
            "The rest of the deck stays in the center as the draw deck.",
            "The throw deck begins empty.",
        ],
    )
    draw_rules_section(
        880,
        150,
        760,
        220,
        "Quick Play",
        [
            "Press Quick Game from home.",
            "The game uses your Settings player count "
            "and joins the first matching room.",
            "Choose A Room lets you browse rooms manually instead.",
        ],
    )
    draw_rules_section(
        60,
        400,
        760,
        220,
        "How To Play",
        [
            "On your turn, left-click cards to select cards "
            "of the same number.",
            "Press T or Enter to throw selected cards.",
            "Click throw deck top to take the pile into your hand.",
            "Right-click Throw clears your current selection.",
        ],
    )
    draw_rules_section(
        880,
        400,
        760,
        220,
        "Win Condition",
        [
            "A player wins by getting rid of all hand, visible, "
            "and secret cards.",
            "The final player left with cards is the ShitHead.",
        ],
    )
    draw_rules_section(
        60,
        650,
        1580,
        270,
        "Special Cards",
        [
            "2: Reset card, can be played freely.",
            "3: Transparent card, follows the previous card rule.",
            "4: Cut-in card, can be thrown out of turn when pile is empty.",
            "8: Skip next player.",
            "10: Burn the throw deck.",
            "Joker (14): Give throw deck to selected player "
            "(or previous player by default).",
        ],
        text_max_width=900,
    )

    pygame.draw.rect(screen, WHITE, (980, 720, 620, 180), 0)
    pygame.draw.rect(screen, BLACK, (980, 720, 620, 180), 2)
    panel_title_font = pygame.font.SysFont("calibri", 28)
    panel_title = panel_title_font.render(
        "Special cards shown in-game", 1, PINK
    )
    screen.blit(panel_title, (1000, 730))

    settings_small = load_scaled_image(SETTINGS, (90, 90), PINK)
    move_left_small = load_scaled_image(MOVE_LEFT, (80, 80), PINK)
    move_right_small = load_scaled_image(MOVE_RIGHT, (80, 80), PINK)
    screen.blit(settings_small, (740, 210))
    screen.blit(move_left_small, (1220, 210))
    screen.blit(move_right_small, (1315, 210))

    special_card_specs = [
        (2, cards.DIAMONDS, "2"),
        (3, cards.CLUBS, "3"),
        (4, cards.HEARTS, "4"),
        (8, cards.SPADES, "8"),
        (10, cards.DIAMONDS, "10"),
        (14, cards.SPADES, "Joker"),
    ]
    card_label_font = pygame.font.SysFont("calibri", 24)
    start_x = 1005
    for index, card_spec in enumerate(special_card_specs):
        num, shape, label = card_spec
        card_image = load_scaled_image(
            cards.CARDSIMAGES[(num, shape)], (82, 102), PINK
        )
        draw_x = start_x + index * 98
        draw_y = 770
        screen.blit(card_image, (draw_x, draw_y))
        label_text = card_label_font.render(label, 1, BLACK)
        screen.blit(label_text, (draw_x + 26, draw_y + 112))

    back = False
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
        if 25 < pos[0] < 25 + 250 and 25 < pos[1] < 25 + 250:
            back = True

    if back:
        return "OPEN_SCREEN"
    return "RULES"


def settings_menu(event: pygame.event.Event, pos: MousePos) -> ScreenState:
    """
    this function is responsible for the settings screen
    :return: None
    """
    global screen

    img = load_image(BACKGROUND)
    screen.blit(img, (0, 0))  # (left, top)
    pygame.display.flip()

    quick_game_settings = button.Button(
        PINK, WINDOW_WIDTH / 2 - 350, 75, 700, 100, "Quick Game Settings"
    )
    number_of_players = button.Button(
        WHITE, WINDOW_WIDTH / 2 - 350, 200, 700, 100, "Number Of Players"
    )

    minus = load_image(MOVE_LEFT, PINK)
    screen.blit(
        minus, (WINDOW_WIDTH / 2 - 110 - 50 - 220, WINDOW_HEIGHT / 2 - 115)
    )

    num = read_preferences_count()

    number = button.Button(
        WHITE,
        WINDOW_WIDTH / 2 - 50,
        WINDOW_HEIGHT / 2 - 50,
        100,
        100,
        str(num),
    )

    plus = load_image(MOVE_RIGHT, PINK)
    screen.blit(plus, (WINDOW_WIDTH / 2 + 110 + 50, WINDOW_HEIGHT / 2 - 115))

    back_button = load_image(ICON, PINK)
    screen.blit(back_button, (25, 25))

    back = False
    red_raw_window(quick_game_settings)
    red_raw_window(number_of_players)
    red_raw_window(number)
    pygame.display.update()

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
        if (
            WINDOW_WIDTH / 2 - 110 - 50 - 220
            < pos[0]
            < WINDOW_WIDTH / 2 - 110 - 50
        ):
            if (
                WINDOW_HEIGHT / 2 - 115
                < pos[1]
                < WINDOW_HEIGHT / 2 - 115 + 230
            ):
                if num > 2:
                    num -= 1
                    write_preferences_count(num)
                    # number = button.Button(WHITE, WINDOW_WIDTH / 2 - 50,
                    # WINDOW_HEIGHT / 2 - 50, 100, 100,
                    #                       str(num))

        elif (
            WINDOW_WIDTH / 2 + 110 + 50
            < pos[0]
            < WINDOW_WIDTH / 2 + 110 + 50 + 220
        ):
            if (
                WINDOW_HEIGHT / 2 - 115
                < pos[1]
                < WINDOW_HEIGHT / 2 - 115 + 230
            ):
                if num < 4:
                    num += 1
                    write_preferences_count(num)
                    # number = button.Button(WHITE, WINDOW_WIDTH / 2 - 50,
                    # WINDOW_HEIGHT / 2 - 50, 100, 100,
                    #                       str(num))

        elif 25 < pos[0] < 25 + 250:
            if 25 < pos[1] < 25 + 250:
                back = True

    if back:
        return "OPEN_SCREEN"
    else:
        return "SETTINGS"


def create_a_room_menu(
    event: pygame.event.Event, pos: MousePos, num: int
) -> ScreenState:
    """
    this function is responsible for creating a private room
    :return:
    """
    global screen

    img = load_image(BACKGROUND)
    screen.blit(img, (0, 0))  # (left, top)
    pygame.display.flip()

    create_a_room_button = button.Button(
        PINK, WINDOW_WIDTH / 2 - 350, 75, 700, 100, "Create A Room"
    )

    minus = load_image(MOVE_LEFT, PINK)
    screen.blit(
        minus, (WINDOW_WIDTH / 2 - 110 - 50 - 220, WINDOW_HEIGHT / 2 - 115)
    )

    number = button.Button(
        WHITE,
        WINDOW_WIDTH / 2 - 50,
        WINDOW_HEIGHT / 2 - 50,
        100,
        100,
        str(num),
    )

    plus = load_image(MOVE_RIGHT, PINK)
    screen.blit(plus, (WINDOW_WIDTH / 2 + 110 + 50, WINDOW_HEIGHT / 2 - 115))

    create = button.Button(
        WHITE, WINDOW_WIDTH / 2 - 350, WINDOW_HEIGHT - 150, 700, 100, "Create"
    )

    back_button = load_image(ICON, PINK)
    screen.blit(back_button, (25, 25))

    back = False
    do_create = False

    red_raw_window(create_a_room_button)
    red_raw_window(number)
    red_raw_window(create)
    pygame.display.update()

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
        if create.is_over(pos):
            do_create = True

            # print 'apply'
        elif (
            WINDOW_WIDTH / 2 - 110 - 50 - 220
            < pos[0]
            < WINDOW_WIDTH / 2 - 110 - 50
        ):
            if (
                WINDOW_HEIGHT / 2 - 115
                < pos[1]
                < WINDOW_HEIGHT / 2 - 115 + 230
            ):
                if num > 2:
                    num -= 1
                    number = button.Button(
                        WHITE,
                        WINDOW_WIDTH / 2 - 50,
                        WINDOW_HEIGHT / 2 - 50,
                        100,
                        100,
                        str(num),
                    )
                    # print 'minus'
        elif (
            WINDOW_WIDTH / 2 + 110 + 50
            < pos[0]
            < WINDOW_WIDTH / 2 + 110 + 50 + 220
        ):
            if (
                WINDOW_HEIGHT / 2 - 115
                < pos[1]
                < WINDOW_HEIGHT / 2 - 115 + 230
            ):
                if num < 4:
                    num += 1
                    number = button.Button(
                        WHITE,
                        WINDOW_WIDTH / 2 - 50,
                        WINDOW_HEIGHT / 2 - 50,
                        100,
                        100,
                        str(num),
                    )
                    # print 'plus'
        elif 25 < pos[0] < 25 + 250:
            if 25 < pos[1] < 25 + 250:
                back = True
                # print 'back'

    if event.type == pygame.MOUSEMOTION:
        if create.is_over(pos):
            create.color = LIGHT_GREY
        else:
            create.color = WHITE

    if do_create:
        SEND.append("SCREEN~CREATE_A_ROOM" + "~" + str(num) + "~~~")
    if back:
        return "OPEN_SCREEN"
    else:
        return "CREATE_A_ROOM", num


def choose_a_room_menu(
    event: pygame.event.Event,
    pos: MousePos,
    games_message: list[str],
    page: int,
) -> ScreenState:
    return choose_room_page.choose_a_room_menu(event, pos, games_message, page)


def join_game(room: int) -> None:
    """
    this function is responsible for joining a game by num_game
    :param room:
    :return: None
    """
    SEND.append("JOIN" + "~" + str(room) + "~~~")


def wait_to_full(
    event: pygame.event.Event,
    pos: MousePos,
    room: int,
    p_now: int,
    people: int,
) -> ScreenState:
    """
    this function is responsible for waiting screen
    :return: None
    """
    global screen

    if not p_now == people:
        img = load_image(BACKGROUND)
        screen.blit(img, (0, 0))  # (left, top)
        pygame.display.flip()

        rn = button.Button(PINK, 2, 2, 400, 100, "ROOM: " + str(room))

        pn = button.Button(
            WHITE,
            WINDOW_WIDTH - 200 - 2,
            2,
            200,
            100,
            str(p_now) + "/" + str(people),
        )

        font = pygame.font.SysFont("algerian", 80)
        text = font.render("waiting for the room to be full...", 1, WHITE)
        screen.blit(
            text,
            (
                WINDOW_WIDTH / 2 - text.get_width() / 2,
                WINDOW_HEIGHT / 2 - text.get_height() / 2,
            ),
        )

        red_raw_window(rn)
        red_raw_window(pn)
        pygame.display.update()

    return "WAITING", room, p_now, people


def game_manager(
    event: pygame.event.Event,
    pos: MousePos,
    cards_message: list[str],
    cards_to_throw: list[cards.Cards],
    to_who: int,
) -> ScreenState:
    return game_page.game_manager(
        event, pos, cards_message, cards_to_throw, to_who
    )


def finish(
    event: pygame.event.Event, pos: MousePos, reason: list[str]
) -> ScreenState:
    """
    this function is responsible for the finish screen
    :param event:
    :param pos:
    :param reason:
    :return:
    """
    global screen

    img = load_image(BACKGROUND)
    screen.blit(img, (0, 0))  # (left, top)
    pygame.display.flip()

    font = pygame.font.SysFont("algerian", 80)
    text = font.render(reason[0], 1, WHITE)
    screen.blit(
        text,
        (
            WINDOW_WIDTH / 2 - text.get_width() / 2,
            WINDOW_HEIGHT / 2 - text.get_height() / 2,
        ),
    )

    back_button = load_image(ICON, PINK)
    screen.blit(back_button, (25, 25))

    back = False

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
        if 25 < pos[0] < 25 + 250:
            if 25 < pos[1] < 25 + 250:
                back = True

    if back:
        return "OPEN_SCREEN"
    else:
        return "FINISH", reason[0]


def async_send_receive(sock: socket.socket) -> None:
    """
    this function is responsible for the sending and receiving with the server
    :param sock: the client's socket :type socket._socketobject
    :return:
    """
    while True:
        try:
            try:
                if SEND:
                    send_with_size(sock, SEND.popleft())

                data = recv_by_size(sock)
                if not data:
                    raise socket.error
                RECEIVE.append(data)

            except socket.timeout:
                continue
        except socket.error:
            break


def event_handler(
    scrn: str,
    pos: MousePos,
    event: pygame.event.Event,
    more_args: Sequence[object],
) -> ScreenState | None:
    """
    this function is responsible for organizing the screens
    :param scrn:
    :param pos:
    :param event:
    :param more_args:
    :return:
    """
    if scrn == "OPEN_SCREEN":
        return open_page.open_screen(event, pos)
    elif scrn == "SETTINGS":
        return settings_page.settings_menu(event, pos)
    elif scrn == "RULES":
        return rules_page.rules_menu(event, pos)
    elif scrn == "RULES_GAME":
        next_screen = rules_page.rules_menu(event, pos, "GAME")
        if next_screen == "GAME":
            return "GAME", more_args[0], more_args[1], more_args[2]
        return "RULES_GAME", more_args[0], more_args[1], more_args[2]
    elif scrn == "CHOOSE_A_ROOM":
        games_message = []
        page = 1
        if len(more_args) >= 1 and isinstance(more_args[0], list):
            games_message = more_args[0]
        if len(more_args) >= 2:
            page = more_args[1]
        return choose_room_page.choose_a_room_menu(
            event, pos, games_message, page
        )
    elif scrn == "CREATE_A_ROOM":
        return create_room_page.create_a_room_menu(event, pos, more_args[0])
    elif scrn == "WAITING":
        return waiting_page.wait_to_full(
            event, pos, more_args[0], more_args[1], more_args[2]
        )
    elif scrn == "GAME":
        return game_page.game_manager(
            event, pos, more_args[0], more_args[1], more_args[2]
        )
    elif scrn == "FINISH":
        return finish_page.finish(event, pos, more_args)
    elif scrn == "CHOOSE_TO_GIVE":
        pass


def receive_handler(recv: str) -> ScreenState | None:
    """
    this function is responsible for handeling with the received messages and
    adding messages to the SEND by the
    protocol.
    :param  :type
    :return:
    """
    print(recv)
    recv = recv[:-2]
    message = recv.split("~")
    # print message
    if message:
        if message[0].upper() == "GAMES" and len(message) >= 2:
            # choose_a_room_menu(message[1:])
            return "CHOOSE_A_ROOM", message[1:], 1
        elif message[0].upper() == "GAME" and len(message) > 2:
            if message[1].upper() == "UPDATE":  # 1st deck
                # game_manager(message[2:])
                return "GAME", message[2:], [], 0
            elif message[1].upper() == "FINISH":
                # finish(message[2])
                return "FINISH", message[2]
        elif message[0].upper() == "UPDATE" and len(message) == 3:
            room = int(message[1].split(",")[0]) + 1
            p_now = int(message[1].split(",")[1])
            people = int(message[1].split(",")[2])
            # wait_to_full(room, p_now, people)
            return "WAITING", room, p_now, people


def red_raw_window(bt: button.Button) -> None:
    bt.draw(screen, (0, 0, 0))
    # pygame.display.update()


def card_to_window(card: cards.Cards) -> None:
    global screen
    card.draw(screen)
    # pygame.display.update()


if __name__ == "__main__":
    main()
