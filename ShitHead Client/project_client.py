import socket
import threading
from collections import deque

import pygame

import button
import cards
import game
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

IP = "127.0.0.1"
PORT = 22073
SEND = deque()
RECEIVE = deque()
THREAD = []
BACKGROUND = "proj_pics/rainbow_background.jpg"  # 1700X956
ICON = "proj_pics/ShitHead_icon_sized.png"  # 250X250
SETTINGS = "proj_pics/settings.png"  # 128X128
MOVE_RIGHT = "proj_pics/move_right.png"  # 220X230
MOVE_LEFT = "proj_pics/move_left.png"  # 220X230
WINDOW_WIDTH = 1700
WINDOW_HEIGHT = 956
PINK = (255, 20, 147)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (2, 251, 146)
LIGHT_GREY = (200, 200, 200)
LEFT = 1
SCROLL = 2
RIGHT = 3
screen = None
IMAGE_CACHE = {}
SCALED_IMAGE_CACHE = {}


def load_image(path, colorkey=None):
    key = (path, colorkey)
    image = IMAGE_CACHE.get(key)
    if image is None:
        image = pygame.image.load(path).convert()
        if colorkey is not None:
            image.set_colorkey(colorkey)
        IMAGE_CACHE[key] = image
    return image


def load_scaled_image(path, size, colorkey=None):
    key = (path, size, colorkey)
    image = SCALED_IMAGE_CACHE.get(key)
    if image is None:
        image = pygame.transform.smoothscale(load_image(path, colorkey), size)
        SCALED_IMAGE_CACHE[key] = image
    return image


def main():
    # Init screen
    global screen
    pygame.init()
    size = (WINDOW_WIDTH, WINDOW_HEIGHT)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()

    img = load_image(BACKGROUND)
    screen.blit(img, (0, 0))  # (left, top)
    pygame.display.flip()
    sock = None
    try:
        sock = socket.socket()
        sock.connect((IP, PORT))
        sock.settimeout(0.1)
        # sock.settimeout(None) #delete the timeout

        send_receive_thread = threading.Thread(
            target=async_send_receive, args=(sock,)
        )
        send_receive_thread.start()
        THREAD.append(send_receive_thread)

        scrn = "OPEN_SCREEN"
        while True:
            clock.tick(60)
            if not send_receive_thread.is_alive():
                raise
                # pass
            if RECEIVE:
                scrn = receive_handler(RECEIVE.popleft())
            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    raise
                    # pass
                else:
                    if type(scrn) is not str:
                        scrn = event_handler(scrn[0], pos, event, scrn[1:])
                    else:
                        scrn = event_handler(scrn, pos, event, [])
            pygame.display.flip()
    except Exception as error:
        print(error)

    try:
        sock.close()
    except socket.error:
        pass
    except TypeError:
        pass

    for th in THREAD:
        th.join()

    pygame.quit()


def open_screen(event, pos):
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
        preferences = ""
        with open("preferences.txt", "r") as f:
            preferences += f.read()
        SEND.append(str(next_screen) + "~" + str(preferences) + "~~~")
    elif next_screen == "CHOOSE_A_ROOM":
        SEND.append("SCREEN~CHOOSE_A_ROOM~~~")
        scrn = "OPEN_SCREEN"
    elif next_screen == "CREATE_A_ROOM":
        num = 0
        try:
            with open("preferences.txt", "r") as f:
                num = int(f.read())
        except IOError:
            num = 2
        scrn = "CREATE_A_ROOM", num
    elif next_screen == "SETTINGS":
        scrn = "SETTINGS"
    elif next_screen == "RULES":
        scrn = "RULES"
    return scrn


def draw_wrapped_lines(font, lines, x, y, max_width, color):
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


def draw_rules_section(x, y, width, height, title, lines):
    pygame.draw.rect(screen, LIGHT_GREY, (x, y, width, height), 0)
    pygame.draw.rect(screen, BLACK, (x, y, width, height), 3)

    title_font = pygame.font.SysFont("calibri", 38)
    body_font = pygame.font.SysFont("calibri", 25)

    title_text = title_font.render(title, 1, PINK)
    screen.blit(title_text, (x + 15, y + 10))

    draw_wrapped_lines(body_font, lines, x + 15, y + 65, width - 30, BLACK)


def rules_menu(event, pos):
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
            "Press T to throw selected cards.",
            "Click throw deck top to take the pile into your hand.",
            "Right-click T clears your current selection.",
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
        260,
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
    )

    settings_small = load_scaled_image(SETTINGS, (90, 90), PINK)
    move_left_small = load_scaled_image(MOVE_LEFT, (80, 80), PINK)
    move_right_small = load_scaled_image(MOVE_RIGHT, (80, 80), PINK)
    screen.blit(settings_small, (740, 210))
    screen.blit(move_left_small, (1220, 210))
    screen.blit(move_right_small, (1315, 210))

    special_cards = [
        cards.Cards(2, cards.DIAMONDS, 1020, 780),
        cards.Cards(3, cards.CLUBS, 1090, 780),
        cards.Cards(4, cards.HEARTS, 1160, 780),
        cards.Cards(8, cards.SPADES, 1230, 780),
        cards.Cards(10, cards.DIAMONDS, 1300, 780),
        cards.Cards(14, cards.SPADES, 1370, 780),
    ]
    for card in special_cards:
        card.draw(screen)

    back = False
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
        if 25 < pos[0] < 25 + 250 and 25 < pos[1] < 25 + 250:
            back = True

    if back:
        return "OPEN_SCREEN"
    return "RULES"


def settings_menu(event, pos):
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

    num = 0
    try:
        with open("preferences.txt", "r") as f:
            num = int(f.read())
    except IOError:
        num = 2

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
                    with open("preferences.txt", "w") as f:
                        f.write(str(num))
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
                    with open("preferences.txt", "w") as f:
                        f.write(str(num))
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


def create_a_room_menu(event, pos, num):
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


def choose_a_room_menu(event, pos, games_message, page):
    """
    this function is responsible for choosing a room to play
    :return:
    """
    global screen
    games = []
    for g in games_message:
        info = g.split(",")
        # print 'info: ' + str(info)
        if len(info) == 3:
            room = game.Game(int(info[0]), int(info[2]), int(info[1]))
            games.append(room)

    img = load_image(BACKGROUND)
    screen.blit(img, (0, 0))  # (left, top)
    pygame.display.flip()

    choose_a_room = button.Button(
        PINK, WINDOW_WIDTH / 2 - 350, 75, 700, 100, "Choose A Room"
    )
    red_raw_window(choose_a_room)

    last_page = load_image(MOVE_LEFT, PINK)
    screen.blit(
        last_page, (WINDOW_WIDTH / 2 - 110 - 50 - 220, WINDOW_HEIGHT - 230)
    )

    num = page
    number = button.Button(
        WHITE, WINDOW_WIDTH / 2 - 50, WINDOW_HEIGHT - 150, 100, 100, str(num)
    )
    red_raw_window(number)

    next_page = load_image(MOVE_RIGHT, PINK)
    screen.blit(next_page, (WINDOW_WIDTH / 2 + 110 + 50, WINDOW_HEIGHT - 230))

    back_button = load_image(ICON, PINK)
    screen.blit(back_button, (25, 25))

    back_to_menu = False
    do_choose = False
    choice = 0

    room1 = None
    room2 = None
    room3 = None
    room4 = None
    room5 = None

    if len(games) >= (num - 1) * 5 + 1:
        room1 = button.Button(
            WHITE,
            WINDOW_WIDTH / 2 - 350,
            200,
            700,
            100,
            "ROOM "
            + str(games[(num - 1) * 5].num_room + 1)
            + " Online: "
            + str(games[(num - 1) * 5].players)
            + "/"
            + str(games[(num - 1) * 5].max_players),
        )
    else:
        room1 = button.Button(
            WHITE,
            WINDOW_WIDTH / 2 - 350,
            200,
            700,
            100,
            "ROOM [" + str((num - 1) * 5 + 1) + "] Online: 0/0",
        )
    red_raw_window(room1)
    if len(games) >= (num - 1) * 5 + 2:
        room2 = button.Button(
            WHITE,
            WINDOW_WIDTH / 2 - 350,
            302,
            700,
            100,
            "ROOM "
            + str(games[(num - 1) * 5 + 1].num_room + 1)
            + " Online: "
            + str(games[(num - 1) * 5 + 1].players)
            + "/"
            + str(games[(num - 1) * 5 + 1].max_players),
        )
    else:
        room2 = button.Button(
            WHITE,
            WINDOW_WIDTH / 2 - 350,
            302,
            700,
            100,
            "ROOM [" + str((num - 1) * 5 + 2) + "] Online: 0/0",
        )
    red_raw_window(room2)
    if len(games) >= (num - 1) * 5 + 3:
        room3 = button.Button(
            WHITE,
            WINDOW_WIDTH / 2 - 350,
            404,
            700,
            100,
            "ROOM "
            + str(games[(num - 1) * 5 + 2].num_room + 1)
            + " Online: "
            + str(games[(num - 1) * 5 + 2].players)
            + "/"
            + str(games[(num - 1) * 5 + 2].max_players),
        )
    else:
        room3 = button.Button(
            WHITE,
            WINDOW_WIDTH / 2 - 350,
            404,
            700,
            100,
            "ROOM [" + str((num - 1) * 5 + 3) + "] Online: 0/0",
        )
    red_raw_window(room3)
    if len(games) >= (num - 1) * 5 + 4:
        room4 = button.Button(
            WHITE,
            WINDOW_WIDTH / 2 - 350,
            506,
            700,
            100,
            "ROOM "
            + str(games[(num - 1) * 5 + 3].num_room + 1)
            + " Online: "
            + str(games[(num - 1) * 5 + 3].players)
            + "/"
            + str(games[(num - 1) * 5 + 3].max_players),
        )
    else:
        room4 = button.Button(
            WHITE,
            WINDOW_WIDTH / 2 - 350,
            506,
            700,
            100,
            "ROOM [" + str((num - 1) * 5 + 4) + "] Online: 0/0",
        )
    red_raw_window(room4)
    if len(games) >= (num - 1) * 5 + 5:
        room5 = button.Button(
            WHITE,
            WINDOW_WIDTH / 2 - 350,
            608,
            700,
            100,
            "ROOM "
            + str(games[(num - 1) * 5 + 4].num_room + 1)
            + " Online: "
            + str(games[(num - 1) * 5 + 4].players)
            + "/"
            + str(games[(num - 1) * 5 + 4].max_players),
        )
    else:
        room5 = button.Button(
            WHITE,
            WINDOW_WIDTH / 2 - 350,
            608,
            700,
            100,
            "ROOM [" + str((num - 1) * 5 + 5) + "] Online: 0/0",
        )
    red_raw_window(room5)

    pygame.display.update()

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
        print("clicked: " + str(pos))
        if room1.is_over(pos):
            if (
                len(games) >= (num - 1) * 5 + 1
                and games[(num - 1) * 5].players
                != games[(num - 1) * 5].max_players
            ):
                choice = games[(num - 1) * 5].num_room
                do_choose = True

        elif room2.is_over(pos):
            if (
                len(games) >= (num - 1) * 5 + 2
                and games[(num - 1) * 5 + 1].players
                != games[(num - 1) * 5 + 1].max_players
            ):
                choice = games[(num - 1) * 5 + 1].num_room
                do_choose = True

        elif room3.is_over(pos):
            if (
                len(games) >= (num - 1) * 5 + 3
                and games[(num - 1) * 5 + 2].players
                != games[(num - 1) * 5 + 2].max_players
            ):
                choice = games[(num - 1) * 5 + 2].num_room
                do_choose = True

        elif room4.is_over(pos):
            if (
                len(games) >= (num - 1) * 5 + 4
                and games[(num - 1) * 5 + 3].players
                != games[(num - 1) * 5 + 3].max_players
            ):
                choice = games[(num - 1) * 5 + 3].num_room
                do_choose = True

        elif room5.is_over(pos):
            if (
                len(games) >= (num - 1) * 5 + 5
                and games[(num - 1) * 5 + 4].players
                != games[(num - 1) * 5 + 4].max_players
            ):
                choice = games[(num - 1) * 5 + 4].num_room
                do_choose = True

        elif (
            WINDOW_WIDTH / 2 - 110 - 50 - 220
            < pos[0]
            < WINDOW_WIDTH / 2 - 110 - 50
        ):
            if WINDOW_HEIGHT - 230 < pos[1] < WINDOW_HEIGHT:
                if num >= 2:
                    num -= 1
                    number = button.Button(
                        WHITE,
                        WINDOW_WIDTH / 2 - 50,
                        WINDOW_HEIGHT / 2 - 50,
                        100,
                        100,
                        str(num),
                    )
                    red_raw_window(number)

                    if len(games) >= (num - 1) * 5 + 1:
                        room1 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            200,
                            700,
                            100,
                            "ROOM "
                            + str(games[(num - 1) * 5].num_room + 1)
                            + " Online: "
                            + str(games[(num - 1) * 5].players)
                            + "/"
                            + str(games[(num - 1) * 5].max_players),
                        )
                    else:
                        room1 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            200,
                            700,
                            100,
                            "ROOM ["
                            + str((num - 1) * 5 + 1)
                            + "] Online: 0/0",
                        )
                    red_raw_window(room1)
                    if len(games) >= (num - 1) * 5 + 2:
                        room2 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            302,
                            700,
                            100,
                            "ROOM "
                            + str(games[(num - 1) * 5 + 1].num_room + 1)
                            + " Online: "
                            + str(games[(num - 1) * 5 + 1].players)
                            + "/"
                            + str(games[(num - 1) * 5 + 1].max_players),
                        )
                    else:
                        room2 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            302,
                            700,
                            100,
                            "ROOM ["
                            + str((num - 1) * 5 + 2)
                            + "] Online: 0/0",
                        )
                    red_raw_window(room2)
                    if len(games) >= (num - 1) * 5 + 3:
                        room3 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            404,
                            700,
                            100,
                            "ROOM "
                            + str(games[(num - 1) * 5 + 2].num_room + 1)
                            + " Online: "
                            + str(games[(num - 1) * 5 + 2].players)
                            + "/"
                            + str(games[(num - 1) * 5 + 2].max_players),
                        )
                    else:
                        room3 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            404,
                            700,
                            100,
                            "ROOM ["
                            + str((num - 1) * 5 + 3)
                            + "] Online: 0/0",
                        )
                    red_raw_window(room3)
                    if len(games) >= (num - 1) * 5 + 4:
                        room4 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            506,
                            700,
                            100,
                            "ROOM "
                            + str(games[(num - 1) * 5 + 3].num_room + 1)
                            + " Online: "
                            + str(games[(num - 1) * 5 + 3].players)
                            + "/"
                            + str(games[(num - 1) * 5 + 3].max_players),
                        )
                    else:
                        room4 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            506,
                            700,
                            100,
                            "ROOM ["
                            + str((num - 1) * 5 + 4)
                            + "] Online: 0/0",
                        )
                    red_raw_window(room4)
                    if len(games) >= (num - 1) * 5 + 5:
                        room5 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            608,
                            700,
                            100,
                            "ROOM "
                            + str(games[(num - 1) * 5 + 4].num_room + 1)
                            + " Online: "
                            + str(games[(num - 1) * 5 + 4].players)
                            + "/"
                            + str(games[(num - 1) * 5 + 4].max_players),
                        )
                    else:
                        room5 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            608,
                            700,
                            100,
                            "ROOM ["
                            + str((num - 1) * 5 + 5)
                            + "] Online: 0/0",
                        )
                    red_raw_window(room5)
                pygame.display.update()
                # print 'minus'
        elif (
            WINDOW_WIDTH / 2 + 110 + 50
            < pos[0]
            < WINDOW_WIDTH / 2 + 110 + 50 + 220
        ):
            if WINDOW_HEIGHT - 230 < pos[1] < WINDOW_HEIGHT:
                if len(games) > num * 5:
                    num += 1
                    number = button.Button(
                        WHITE,
                        WINDOW_WIDTH / 2 - 50,
                        WINDOW_HEIGHT / 2 - 50,
                        100,
                        100,
                        str(num),
                    )
                    red_raw_window(number)

                    if len(games) >= (num - 1) * 5 + 1:
                        room1 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            200,
                            700,
                            100,
                            "ROOM "
                            + str(games[(num - 1) * 5].num_room + 1)
                            + " Online: "
                            + str(games[(num - 1) * 5].players)
                            + "/"
                            + str(games[(num - 1) * 5].max_players),
                        )
                    else:
                        room1 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            200,
                            700,
                            100,
                            "ROOM ["
                            + str((num - 1) * 5 + 1)
                            + "] Online: 0/0",
                        )
                    red_raw_window(room1)
                    if len(games) >= (num - 1) * 5 + 2:
                        room2 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            302,
                            700,
                            100,
                            "ROOM "
                            + str(games[(num - 1) * 5 + 1].num_room + 1)
                            + " Online: "
                            + str(games[(num - 1) * 5 + 1].players)
                            + "/"
                            + str(games[(num - 1) * 5 + 1].max_players),
                        )
                    else:
                        room2 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            302,
                            700,
                            100,
                            "ROOM ["
                            + str((num - 1) * 5 + 2)
                            + "] Online: 0/0",
                        )
                    red_raw_window(room2)
                    if len(games) >= (num - 1) * 5 + 3:
                        room3 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            404,
                            700,
                            100,
                            "ROOM "
                            + str(games[(num - 1) * 5 + 2].num_room + 1)
                            + " Online: "
                            + str(games[(num - 1) * 5 + 2].players)
                            + "/"
                            + str(games[(num - 1) * 5 + 2].max_players),
                        )
                    else:
                        room3 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            404,
                            700,
                            100,
                            "ROOM ["
                            + str((num - 1) * 5 + 3)
                            + "] Online: 0/0",
                        )
                    red_raw_window(room3)
                    if len(games) >= (num - 1) * 5 + 4:
                        room4 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            506,
                            700,
                            100,
                            "ROOM "
                            + str(games[(num - 1) * 5 + 3].num_room + 1)
                            + " Online: "
                            + str(games[(num - 1) * 5 + 3].players)
                            + "/"
                            + str(games[(num - 1) * 5 + 3].max_players),
                        )
                    else:
                        room4 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            506,
                            700,
                            100,
                            "ROOM ["
                            + str((num - 1) * 5 + 4)
                            + "] Online: 0/0",
                        )
                    red_raw_window(room4)
                    if len(games) >= (num - 1) * 5 + 5:
                        room5 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            608,
                            700,
                            100,
                            "ROOM "
                            + str(games[(num - 1) * 5 + 4].num_room + 1)
                            + " Online: "
                            + str(games[(num - 1) * 5 + 4].players)
                            + "/"
                            + str(games[(num - 1) * 5 + 4].max_players),
                        )
                    else:
                        room5 = button.Button(
                            WHITE,
                            WINDOW_WIDTH / 2 - 350,
                            608,
                            700,
                            100,
                            "ROOM ["
                            + str((num - 1) * 5 + 5)
                            + "] Online: 0/0",
                        )
                    red_raw_window(room5)
                pygame.display.update()
                # print 'plus'
        elif 25 < pos[0] < 25 + 250:
            if 25 < pos[1] < 25 + 250:
                back_to_menu = True

    elif event.type == pygame.MOUSEMOTION:
        if room1.is_over(pos):
            room1.color = LIGHT_GREY
        else:
            room1.color = WHITE
        if room2.is_over(pos):
            room2.color = LIGHT_GREY
        else:
            room2.color = WHITE
        if room3.is_over(pos):
            room3.color = LIGHT_GREY
        else:
            room3.color = WHITE
        if room4.is_over(pos):
            room4.color = LIGHT_GREY
        else:
            room4.color = WHITE
        if room5.is_over(pos):
            room5.color = LIGHT_GREY
        else:
            room5.color = WHITE
        red_raw_window(room1)
        red_raw_window(room2)
        red_raw_window(room3)
        red_raw_window(room4)
        red_raw_window(room5)
        pygame.display.update()

    if back_to_menu:
        return "OPEN_SCREEN"
    elif do_choose:
        join_game(choice)
    return "CHOOSE_A_ROOM", games_message, num


def join_game(room):
    """
    this function is responsible for joining a game by num_game
    :param room:
    :return: None
    """
    SEND.append("JOIN" + "~" + str(room) + "~~~")


def wait_to_full(event, pos, room, p_now, people):
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


def game_manager(event, pos, cards_message, cards_to_throw, to_who):
    """
    this function is responsible for playing the game
    :param event:
    :param pos:
    :param cards_message:
    :param cards_to_throw:
    :param to_who:
    :return:
    """
    global screen
    # print 'printing game'

    img = load_image(BACKGROUND)
    screen.blit(img, (0, 0))  # (left, top)
    pygame.display.flip()

    deck_card = None
    top_card = None
    deck = int(cards_message[0])
    if deck > 0:
        deck_card = cards.Cards(
            None, None, WINDOW_WIDTH / 2 + 50, WINDOW_HEIGHT / 2 - 125 + 10
        )
        deck_button = button.Button(
            WHITE,
            WINDOW_WIDTH / 2 + 50 + 200 + 2,
            WINDOW_HEIGHT / 2 - 50 + 10,
            100,
            100,
            str(deck),
        )
        card_to_window(deck_card)
        red_raw_window(deck_button)

    deck_top_number = int(cards_message[1].split(",")[0])
    deck_top_shape = int(cards_message[1].split(",")[1])
    if deck_top_number != 0:
        top_card = cards.Cards(
            deck_top_number,
            deck_top_shape,
            WINDOW_WIDTH / 2 - 250,
            WINDOW_HEIGHT / 2 - 125 + 10,
        )
        card_to_window(top_card)

    cards_str = cards_message[2].split(":")[1].split("|")
    hand = []
    for card in cards_str:
        if card != "":
            hand.append((int(card.split(",")[0]), int(card.split(",")[1])))

    if hand:
        start_draw_hand = WINDOW_WIDTH / 2 - (len(hand) / 2) * 40 - 100
        for i in range(len(hand)):
            in_throw = False
            for card in cards_to_throw:
                if (
                    card.get_number() == hand[i][0]
                    and card.get_shape() == hand[i][1]
                ):
                    in_throw = True
            if in_throw:
                hand[i] = cards.Cards(
                    hand[i][0],
                    hand[i][1],
                    start_draw_hand,
                    WINDOW_HEIGHT - 90 - 10,
                )
            else:
                hand[i] = cards.Cards(
                    hand[i][0], hand[i][1], start_draw_hand, WINDOW_HEIGHT - 90
                )
            start_draw_hand += 40
            card_to_window(hand[i])

    visible = []
    cards_str = cards_message[3].split(":")[1].split("|")
    for card in cards_str:
        if card != "":
            visible.append((int(card.split(",")[0]), int(card.split(",")[1])))

    secret = int(cards_message[4].split(":")[1])

    secrets = []
    if secret == 1:
        secrets.append(
            cards.Cards(
                None,
                None,
                WINDOW_WIDTH / 2 - 100 - 20,
                WINDOW_HEIGHT - 92 - 250,
            )
        )
    elif secret == 2:
        secrets.append(
            cards.Cards(
                None,
                None,
                WINDOW_WIDTH / 2 - 250 - 20,
                WINDOW_HEIGHT - 92 - 250,
            )
        )
        secrets.append(
            cards.Cards(
                None,
                None,
                WINDOW_WIDTH / 2 + 50 - 20,
                WINDOW_HEIGHT - 92 - 250,
            )
        )
    elif secret == 3:
        secrets.append(
            cards.Cards(
                None,
                None,
                WINDOW_WIDTH / 2 - 350 - 20,
                WINDOW_HEIGHT - 92 - 250,
            )
        )
        secrets.append(
            cards.Cards(
                None,
                None,
                WINDOW_WIDTH / 2 - 100 - 20,
                WINDOW_HEIGHT - 92 - 250,
            )
        )
        secrets.append(
            cards.Cards(
                None,
                None,
                WINDOW_WIDTH / 2 + 150 - 20,
                WINDOW_HEIGHT - 92 - 250,
            )
        )
    for card in secrets:
        card_to_window(card)

    if len(visible) == 1:
        in_throw = False
        for card in cards_to_throw:
            if (
                card.get_number() == visible[0][0]
                and card.get_shape() == visible[0][1]
            ):
                in_throw = True
        if in_throw:
            visible[0] = cards.Cards(
                visible[0][0],
                visible[0][1],
                WINDOW_WIDTH / 2 - 100,
                WINDOW_HEIGHT - 92 - 250 - 10,
            )
        else:
            visible[0] = cards.Cards(
                visible[0][0],
                visible[0][1],
                WINDOW_WIDTH / 2 - 100,
                WINDOW_HEIGHT - 92 - 250,
            )
    elif len(visible) == 2:
        in_throw = False
        for card in cards_to_throw:
            if (
                card.get_number() == visible[0][0]
                and card.get_shape() == visible[0][1]
            ):
                in_throw = True
        if in_throw:
            visible[0] = cards.Cards(
                visible[0][0],
                visible[0][1],
                WINDOW_WIDTH / 2 - 250,
                WINDOW_HEIGHT - 92 - 250 - 10,
            )
        else:
            visible[0] = cards.Cards(
                visible[0][0],
                visible[0][1],
                WINDOW_WIDTH / 2 - 250,
                WINDOW_HEIGHT - 92 - 250,
            )
        in_throw = False
        for card in cards_to_throw:
            if (
                card.get_number() == visible[1][0]
                and card.get_shape() == visible[1][1]
            ):
                in_throw = True
        if in_throw:
            visible[1] = cards.Cards(
                visible[1][0],
                visible[1][1],
                WINDOW_WIDTH / 2 + 50,
                WINDOW_HEIGHT - 92 - 250 - 10,
            )
        else:
            visible[1] = cards.Cards(
                visible[1][0],
                visible[1][1],
                WINDOW_WIDTH / 2 + 50,
                WINDOW_HEIGHT - 92 - 250,
            )
    elif len(visible) == 3:
        in_throw = False
        for card in cards_to_throw:
            if (
                card.get_number() == visible[0][0]
                and card.get_shape() == visible[0][1]
            ):
                in_throw = True
        if in_throw:
            visible[0] = cards.Cards(
                visible[0][0],
                visible[0][1],
                WINDOW_WIDTH / 2 - 350,
                WINDOW_HEIGHT - 92 - 250 - 10,
            )
        else:
            visible[0] = cards.Cards(
                visible[0][0],
                visible[0][1],
                WINDOW_WIDTH / 2 - 350,
                WINDOW_HEIGHT - 92 - 250,
            )
        in_throw = False
        for card in cards_to_throw:
            if (
                card.get_number() == visible[1][0]
                and card.get_shape() == visible[1][1]
            ):
                in_throw = True
        if in_throw:
            visible[1] = cards.Cards(
                visible[1][0],
                visible[1][1],
                WINDOW_WIDTH / 2 - 100,
                WINDOW_HEIGHT - 92 - 250 - 10,
            )
        else:
            visible[1] = cards.Cards(
                visible[1][0],
                visible[1][1],
                WINDOW_WIDTH / 2 - 100,
                WINDOW_HEIGHT - 92 - 250,
            )
        in_throw = False
        for card in cards_to_throw:
            if (
                card.get_number() == visible[2][0]
                and card.get_shape() == visible[2][1]
            ):
                in_throw = True
        if in_throw:
            visible[2] = cards.Cards(
                visible[2][0],
                visible[2][1],
                WINDOW_WIDTH / 2 + 150,
                WINDOW_HEIGHT - 92 - 250 - 10,
            )
        else:
            visible[2] = cards.Cards(
                visible[2][0],
                visible[2][1],
                WINDOW_WIDTH / 2 + 150,
                WINDOW_HEIGHT - 92 - 250,
            )
    for card in visible:
        card_to_window(card)

    throw_button = button.Button(
        WHITE, WINDOW_WIDTH / 2 - 50, WINDOW_HEIGHT / 2 + 10, 100, 100, "T"
    )
    red_raw_window(throw_button)

    turn = int(cards_message[5].split(":")[1]) + 1
    turn_button = button.Button(
        RED,
        WINDOW_WIDTH / 2 - 50,
        WINDOW_HEIGHT / 2 - 100 + 10,
        100,
        100,
        str(turn),
    )
    red_raw_window(turn_button)

    other_players_data = {}
    players_num = []
    add_to = 0
    for part in cards_message[6:]:
        if part.split(":")[0] == "Player":
            add_to = int(part.split(":")[1])
            other_players_data[add_to] = []
            players_num.append(add_to)
        elif part.split(":")[0] == "Hand":
            other_players_data[add_to].append(int(part.split(":")[1]))
        elif part.split(":")[0] == "Visible":
            vis = []
            cards_str = part.split(":")[1].split("|")
            for card in cards_str:
                if card != "":
                    vis.append(
                        (int(card.split(",")[0]), int(card.split(",")[1]))
                    )
            other_players_data[add_to].append(vis)
        elif part.split(":")[0] == "Secret":
            other_players_data[add_to].append(int(part.split(":")[1]))

    num_cards_player_buttons = []
    num_player_buttons = []
    players_cards_secret = []
    players_cards_visible = []
    if len(other_players_data) >= 1:
        num_cards_player_buttons.append(
            button.Button(
                WHITE,
                WINDOW_WIDTH / 2,
                2,
                100,
                100,
                str(other_players_data[players_num[0]][0]),
            )
        )
        num_player_buttons.append(
            button.Button(
                PINK, WINDOW_WIDTH / 2 - 100, 2, 100, 100, str(players_num[0])
            )
        )
        lst_secret = []
        if other_players_data[players_num[0]][2] >= 1:
            lst_secret.append(
                cards.Cards(None, None, WINDOW_WIDTH / 2 - 350 - 20, 112)
            )
        if other_players_data[players_num[0]][2] >= 2:
            lst_secret.append(
                cards.Cards(None, None, WINDOW_WIDTH / 2 - 100 - 20, 112)
            )
        if other_players_data[players_num[0]][2] == 3:
            lst_secret.append(
                cards.Cards(None, None, WINDOW_WIDTH / 2 + 150 - 20, 112)
            )
        lst_visible = []
        if len(other_players_data[players_num[0]][1]) >= 1:
            lst_visible.append(
                cards.Cards(
                    other_players_data[players_num[0]][1][0][0],
                    other_players_data[players_num[0]][1][0][1],
                    WINDOW_WIDTH / 2 - 350,
                    112,
                )
            )
        if len(other_players_data[players_num[0]][1]) >= 2:
            lst_visible.append(
                cards.Cards(
                    other_players_data[players_num[0]][1][1][0],
                    other_players_data[players_num[0]][1][1][1],
                    WINDOW_WIDTH / 2 - 100,
                    112,
                )
            )
        if len(other_players_data[players_num[0]][1]) == 3:
            lst_visible.append(
                cards.Cards(
                    other_players_data[players_num[0]][1][2][0],
                    other_players_data[players_num[0]][1][2][1],
                    WINDOW_WIDTH / 2 + 150,
                    112,
                )
            )
        players_cards_secret.append(lst_secret)
        players_cards_visible.append(lst_visible)

    if len(other_players_data) >= 2:
        num_cards_player_buttons.append(
            button.Button(
                WHITE,
                2,
                WINDOW_HEIGHT / 2 - 52,
                100,
                100,
                str(other_players_data[players_num[1]][0]),
            )
        )
        num_player_buttons.append(
            button.Button(
                PINK, 2, WINDOW_HEIGHT / 2 + 52, 100, 100, str(players_num[1])
            )
        )
        lst_secret = []
        if other_players_data[players_num[1]][2] >= 1:
            lst_secret.append(
                cards.Cards(
                    None,
                    None,
                    WINDOW_WIDTH / 2 - 500 - 200 - 20 - 20,
                    WINDOW_HEIGHT / 2 - 125 - 250 - 20 - 20,
                )
            )
        if other_players_data[players_num[1]][2] >= 2:
            lst_secret.append(
                cards.Cards(
                    None,
                    None,
                    WINDOW_WIDTH / 2 - 500 - 200 - 20 - 20,
                    WINDOW_HEIGHT / 2 - 125,
                )
            )
        if other_players_data[players_num[1]][2] == 3:
            lst_secret.append(
                cards.Cards(
                    None,
                    None,
                    WINDOW_WIDTH / 2 - 500 - 200 - 20 - 20,
                    WINDOW_HEIGHT / 2 + 125 + 20 + 20,
                )
            )
        lst_visible = []
        if len(other_players_data[players_num[1]][1]) >= 1:
            lst_visible.append(
                cards.Cards(
                    other_players_data[players_num[1]][1][0][0],
                    other_players_data[players_num[1]][1][0][1],
                    WINDOW_WIDTH / 2 - 500 - 200 - 20,
                    WINDOW_HEIGHT / 2 - 125 - 250 - 20 - 20,
                )
            )
        if len(other_players_data[players_num[1]][1]) >= 2:
            lst_visible.append(
                cards.Cards(
                    other_players_data[players_num[1]][1][1][0],
                    other_players_data[players_num[1]][1][1][1],
                    WINDOW_WIDTH / 2 - 500 - 200 - 20,
                    WINDOW_HEIGHT / 2 - 125,
                )
            )
        if len(other_players_data[players_num[1]][1]) == 3:
            lst_visible.append(
                cards.Cards(
                    other_players_data[players_num[1]][1][2][0],
                    other_players_data[players_num[1]][1][2][1],
                    WINDOW_WIDTH / 2 - 500 - 200 - 20,
                    WINDOW_HEIGHT / 2 + 125 + 20 + 20,
                )
            )
        players_cards_secret.append(lst_secret)
        players_cards_visible.append(lst_visible)

    if len(other_players_data) >= 3:
        num_cards_player_buttons.append(
            button.Button(
                WHITE,
                WINDOW_WIDTH - 102,
                WINDOW_HEIGHT / 2 - 52,
                100,
                100,
                str(other_players_data[players_num[2]][0]),
            )
        )
        num_player_buttons.append(
            button.Button(
                PINK,
                WINDOW_WIDTH - 102,
                WINDOW_HEIGHT / 2 + 52,
                100,
                100,
                str(players_num[2]),
            )
        )
        lst_secret = []
        if other_players_data[players_num[2]][2] >= 1:
            lst_secret.append(
                cards.Cards(
                    None,
                    None,
                    WINDOW_WIDTH / 2 + 500 + 20 - 20,
                    WINDOW_HEIGHT / 2 - 125 - 250 - 20 - 20,
                )
            )
        if other_players_data[players_num[2]][2] >= 2:
            lst_secret.append(
                cards.Cards(
                    None,
                    None,
                    WINDOW_WIDTH / 2 + 500 + 20 - 20,
                    WINDOW_HEIGHT / 2 - 125,
                )
            )
        if other_players_data[players_num[2]][2] == 3:
            lst_secret.append(
                cards.Cards(
                    None,
                    None,
                    WINDOW_WIDTH / 2 + 500 + 20 - 20,
                    WINDOW_HEIGHT / 2 + 125 + 20 + 20,
                )
            )
        lst_visible = []
        if len(other_players_data[players_num[2]][1]) >= 1:
            lst_visible.append(
                cards.Cards(
                    other_players_data[players_num[2]][1][0][0],
                    other_players_data[players_num[2]][1][0][1],
                    WINDOW_WIDTH / 2 + 500 + 20,
                    WINDOW_HEIGHT / 2 - 125 - 250 - 20 - 20,
                )
            )
        if len(other_players_data[players_num[2]][1]) >= 2:
            lst_visible.append(
                cards.Cards(
                    other_players_data[players_num[2]][1][1][0],
                    other_players_data[players_num[2]][1][1][1],
                    WINDOW_WIDTH / 2 + 500 + 20,
                    WINDOW_HEIGHT / 2 - 125,
                )
            )
        if len(other_players_data[players_num[2]][1]) == 3:
            lst_visible.append(
                cards.Cards(
                    other_players_data[players_num[2]][1][2][0],
                    other_players_data[players_num[2]][1][2][1],
                    WINDOW_WIDTH / 2 + 500 + 20,
                    WINDOW_HEIGHT / 2 + 125 + 20 + 20,
                )
            )
        players_cards_secret.append(lst_secret)
        players_cards_visible.append(lst_visible)

    for b in num_cards_player_buttons:
        red_raw_window(b)
    for b in num_player_buttons:
        red_raw_window(b)
    for dk in players_cards_secret:
        for c in dk:
            card_to_window(c)
    for dk in players_cards_visible:
        for c in dk:
            card_to_window(c)

    send = False
    message = "GAME~"

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
        for num_player_button in num_player_buttons:
            if num_player_button.is_over(pos):
                to_who = int(num_player_button.text)
        if throw_button.is_over(pos):
            if cards_to_throw:
                message += "THROW~"
                for card in cards_to_throw:
                    message += (
                        str(card.get_number())
                        + ","
                        + str(card.get_shape())
                        + "|"
                    )
                message += "~"
                message += str(to_who)
                message += "~~~"
                send = True
        if top_card and top_card.is_over(pos):
            message += "TAKE_DECK_TO_HAND~~~"
            send = True
        elif hand and len(cards_to_throw) != len(hand) or deck != 0:
            for cr in reversed(hand):
                if cr.is_over(pos):
                    if (
                        not cards_to_throw
                        or cards_to_throw[0].get_number() == cr.get_number()
                    ):
                        can_remove = True
                        for c in cards_to_throw:
                            if c.get_shape() == cr.get_shape():
                                can_remove = False
                        if can_remove:
                            cards_to_throw.append(cr)

        elif visible:
            # found = 0
            for cr in visible:
                if cr.is_over(pos):
                    if (
                        not cards_to_throw
                        or cards_to_throw[0].get_number() == cr.get_number()
                    ):
                        can_remove = True
                        for c in cards_to_throw:
                            if c.get_shape() == cr.get_shape():
                                can_remove = False
                        if can_remove:
                            cards_to_throw.append(cr)

        elif secret:
            for cr in secrets:
                if cr.is_over(pos):
                    message += "THROW~~~"
                    send = True

        pygame.display.update()

    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == RIGHT:
        if throw_button.is_over(pos):
            cards_to_throw = []
            to_who = 0

        if hand:
            for cr in reversed(hand):
                if cr.is_over(pos):
                    if (
                        cards_to_throw
                        and cards_to_throw[0].get_number() == cr.get_number()
                    ):
                        can_remove = False
                        card_to_remove = None
                        for c in cards_to_throw:
                            if c.get_shape() == cr.get_shape():
                                can_remove = True
                                card_to_remove = c
                        if can_remove:
                            cards_to_throw.remove(card_to_remove)

        elif visible:
            # found = 0
            for cr in visible:
                if cr.is_over(pos):
                    if (
                        cards_to_throw
                        and cards_to_throw[0].get_number() == cr.get_number()
                    ):
                        can_remove = False
                        card_to_remove = None
                        for c in cards_to_throw:
                            if c.get_shape() == cr.get_shape():
                                can_remove = True
                                card_to_remove = c
                        if can_remove:
                            cards_to_throw.remove(card_to_remove)
        pygame.display.update()

    if send:
        SEND.append(message)
        return "GAME", cards_message, [], 0
    return "GAME", cards_message, cards_to_throw, to_who


def finish(event, pos, reason):
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


def async_send_receive(sock):
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


def event_handler(scrn, pos, event, more_args):
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
    elif scrn == "CHOOSE_A_ROOM":
        return choose_room_page.choose_a_room_menu(
            event, pos, more_args[0], more_args[1]
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


def receive_handler(recv):
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


def red_raw_window(bt):
    bt.draw(screen, (0, 0, 0))
    # pygame.display.update()


def card_to_window(card):
    global screen
    card.draw(screen)
    # pygame.display.update()


if __name__ == "__main__":
    main()
