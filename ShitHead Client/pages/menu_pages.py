import pygame
from typing import Optional, TypeAlias

from pages._client_ref import get_client_module

MousePos: TypeAlias = tuple[float, float]
ScreenState: TypeAlias = str | tuple[object, ...]
RULES_SCROLL_OFFSET = 0
SETTINGS_HOST_INPUT: Optional[str] = None
SETTINGS_PORT_INPUT: Optional[str] = None
SETTINGS_ACTIVE_FIELD: Optional[str] = None
SETTINGS_STATUS_TEXT: str = ""


def draw_wrapped_lines(
    font: pygame.font.Font,
    lines: list[str],
    x: float,
    y: float,
    max_width: float,
    color: tuple[int, int, int],
) -> float:
    pc = get_client_module()
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
                pc.screen.blit(text, (x, current_y))
                current_y += line_height + line_space
                current_line = word
        if current_line:
            text = font.render(current_line, 1, color)
            pc.screen.blit(text, (x, current_y))
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
    pc = get_client_module()
    pygame.draw.rect(pc.screen, pc.LIGHT_GREY, (x, y, width, height), 0)
    pygame.draw.rect(pc.screen, pc.BLACK, (x, y, width, height), 3)

    title_font = pygame.font.SysFont("calibri", 38)
    body_font = pygame.font.SysFont("calibri", 25)

    title_text = title_font.render(title, 1, pc.PINK)
    pc.screen.blit(title_text, (x + 15, y + 10))

    if text_max_width is None:
        text_max_width = width - 30

    draw_wrapped_lines(
        body_font, lines, x + 15, y + 65, text_max_width, pc.BLACK
    )


def draw_page_top_bar(
    title_text: str,
    header_height: int = 130,
    subtitle_text: Optional[str] = None,
) -> pygame.Rect:
    pc = get_client_module()

    pygame.draw.rect(
        pc.screen, pc.LIGHT_GREY, (0, 0, pc.WINDOW_WIDTH, header_height)
    )
    pygame.draw.rect(
        pc.screen,
        pc.BLACK,
        (0, header_height - 1, pc.WINDOW_WIDTH, 3),
    )

    title_font = pygame.font.SysFont("calibri", 54, bold=True)
    title = title_font.render(title_text, 1, pc.PINK)
    pc.screen.blit(title, (pc.WINDOW_WIDTH / 2 - title.get_width() / 2, 26))

    if subtitle_text:
        subtitle_font = pygame.font.SysFont("calibri", 26)
        subtitle = subtitle_font.render(subtitle_text, 1, pc.BLACK)
        pc.screen.blit(
            subtitle,
            (
                pc.WINDOW_WIDTH / 2 - subtitle.get_width() / 2,
                header_height - subtitle.get_height() - 8,
            ),
        )

    back_button = pc.button.Button(pc.WHITE, 25, 26, 210, 72, "Back")
    pc.red_raw_window(back_button)
    return pygame.Rect(25, 26, 210, 72)


def open_screen(event: pygame.event.Event, pos: MousePos) -> ScreenState:
    pc = get_client_module()

    img = pc.load_image(pc.BACKGROUND)
    pc.screen.blit(img, (0, 0))

    quick_game = pc.button.Button(
        pc.WHITE, pc.WINDOW_WIDTH / 2 - 350, 75, 700, 100, "Quick Game"
    )

    connect_button = pc.button.Button(
        pc.WHITE,
        25,
        pc.WINDOW_HEIGHT - 110,
        300,
        70,
        "Connect",
        font_size=42,
    )

    settings = pc.load_image(pc.SETTINGS, pc.PINK)
    pc.screen.blit(settings, (pc.WINDOW_WIDTH - 150, 22))

    icon = pc.load_image(pc.ICON, pc.PINK)
    pc.screen.blit(icon, (pc.WINDOW_WIDTH / 2 - 125, 190))

    choose_a_room = pc.button.Button(
        pc.WHITE, pc.WINDOW_WIDTH / 2 - 350, 440, 700, 100, "Choose A Room"
    )
    create_a_room = pc.button.Button(
        pc.WHITE, pc.WINDOW_WIDTH / 2 - 350, 590, 700, 100, "Create A Room"
    )
    rules = pc.button.Button(
        pc.WHITE, pc.WINDOW_WIDTH / 2 - 350, 740, 700, 100, "Game Rules"
    )

    next_screen = ""
    pc.red_raw_window(quick_game)
    pc.red_raw_window(choose_a_room)
    pc.red_raw_window(create_a_room)
    pc.red_raw_window(rules)
    pc.red_raw_window(connect_button)

    status_font = pygame.font.SysFont("calibri", 30)
    status_text = status_font.render(pc.get_connection_status(), 1, pc.WHITE)
    pc.screen.blit(status_text, (340, pc.WINDOW_HEIGHT - 98))

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == pc.LEFT:
        if quick_game.is_over(pos):
            next_screen = "QUICK_GAME"

        elif choose_a_room.is_over(pos):
            next_screen = "CHOOSE_A_ROOM"

        elif create_a_room.is_over(pos):
            next_screen = "CREATE_A_ROOM"

        elif rules.is_over(pos):
            next_screen = "RULES"

        elif connect_button.is_over(pos):
            pc.connect_to_server()
            next_screen = "OPEN_SCREEN"

        elif pc.WINDOW_WIDTH - 150 < pos[0] < pc.WINDOW_WIDTH - 150 + 128:
            if 22 < pos[1] < 22 + 128:
                next_screen = "SETTINGS"
        else:
            next_screen = "OPEN_SCREEN"

    if event.type == pygame.MOUSEMOTION:
        if quick_game.is_over(pos):
            quick_game.color = pc.LIGHT_GREY
        else:
            quick_game.color = pc.WHITE
        if choose_a_room.is_over(pos):
            choose_a_room.color = pc.LIGHT_GREY
        else:
            choose_a_room.color = pc.WHITE
        if create_a_room.is_over(pos):
            create_a_room.color = pc.LIGHT_GREY
        else:
            create_a_room.color = pc.WHITE
        if rules.is_over(pos):
            rules.color = pc.LIGHT_GREY
        else:
            rules.color = pc.WHITE
        if connect_button.is_over(pos):
            connect_button.color = pc.LIGHT_GREY
        else:
            connect_button.color = pc.WHITE

    scrn: ScreenState = "OPEN_SCREEN"
    if next_screen == "QUICK_GAME":
        if not pc.is_connected():
            ok, _ = pc.connect_to_server()
            if not ok:
                return "OPEN_SCREEN"
        preferences = str(pc.read_preferences_count())
        pc.SEND.append(str(next_screen) + "~" + str(preferences) + "~~~")
    elif next_screen == "CHOOSE_A_ROOM":
        if not pc.is_connected():
            ok, _ = pc.connect_to_server()
            if not ok:
                return "OPEN_SCREEN"
        pc.SEND.append("SCREEN~CHOOSE_A_ROOM~~~")
        scrn = "OPEN_SCREEN"
    elif next_screen == "CREATE_A_ROOM":
        if not pc.is_connected():
            ok, _ = pc.connect_to_server()
            if not ok:
                return "OPEN_SCREEN"
        num = pc.read_preferences_count()
        scrn = "CREATE_A_ROOM", num
    elif next_screen == "SETTINGS":
        scrn = "SETTINGS"
    elif next_screen == "RULES":
        scrn = "RULES"
    return scrn


def rules_menu(
    event: pygame.event.Event,
    pos: MousePos,
    return_screen: str = "OPEN_SCREEN",
) -> ScreenState:
    global RULES_SCROLL_OFFSET

    pc = get_client_module()

    img = pc.load_image(pc.BACKGROUND)
    pc.screen.blit(img, (0, 0))

    header_height = 130
    content_top = header_height
    max_scroll_offset = 0
    min_scroll_offset = -460
    scroll_step = 24

    if event.type == pygame.MOUSEWHEEL:
        RULES_SCROLL_OFFSET += event.y * scroll_step
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
        RULES_SCROLL_OFFSET += scroll_step
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
        RULES_SCROLL_OFFSET -= scroll_step

    if RULES_SCROLL_OFFSET > max_scroll_offset:
        RULES_SCROLL_OFFSET = max_scroll_offset
    if RULES_SCROLL_OFFSET < min_scroll_offset:
        RULES_SCROLL_OFFSET = min_scroll_offset

    y_shift = RULES_SCROLL_OFFSET

    draw_rules_section(
        60,
        170 + y_shift,
        760,
        220,
        "Setup Game",
        [
            "Each player starts with 3 secret face-down cards, "
            "3 visible face-up cards, and 3 cards in hand.",
            "You must use cards in this order: hand first, then visible, "
            "then secret.",
            "The middle deck is the draw deck, and the throw pile starts "
            "empty.",
        ],
    )
    draw_rules_section(
        880,
        170 + y_shift,
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
        430 + y_shift,
        760,
        280,
        "Your Turn (Step-by-Step)",
        [
            "1) Select one or more cards of the same rank (left-click).",
            "2) Press T or Enter or the Throw button to throw them.",
            "3) If your hand is empty, play from visible cards. "
            "If both are empty, click a secret card.",
            "4) If you cannot play, click the throw pile to take it "
            "into your hand.",
            "Right-click the Thorw button clears your current selection.",
        ],
    )
    draw_rules_section(
        880,
        430 + y_shift,
        760,
        280,
        "After You Play",
        [
            "If the throw is valid, your cards go to the throw pile.",
            "If you played from hand and draw cards are left, "
            "you automatically draw back up to 3 cards.",
            "Turn usually passes to the next player "
            "(special cards can change this).",
            "First player with no hand, visible, or secret cards wins.",
            "Last player still holding cards is the ShitHead.",
        ],
    )
    draw_rules_section(
        60,
        760 + y_shift,
        1580,
        320,
        "Special Cards",
        [
            "2: Wild reset (always legal to play).",
            "3: Transparent (does not change what rank is required).",
            "4: Cut-in card (can be played out of turn only when pile is "
            "empty).",
            "7: Next play must be 7 or lower (except special cards).",
            "8: Skip the next player.",
            "10: Burn the throw pile (pile is cleared).",
            "Joker / 14: Give the throw pile to chosen player "
            "(or previous player if none chosen).",
        ],
        text_max_width=1200,
    )

    panel_x = 60
    panel_y = 1120 + y_shift
    panel_width = 1580
    panel_height = 220
    pygame.draw.rect(
        pc.screen, pc.WHITE, (panel_x, panel_y, panel_width, panel_height), 0
    )
    pygame.draw.rect(
        pc.screen, pc.BLACK, (panel_x, panel_y, panel_width, panel_height), 2
    )
    panel_title_font = pygame.font.SysFont("calibri", 30)
    panel_title = panel_title_font.render(
        "Special cards shown in-game", 1, pc.PINK
    )
    pc.screen.blit(panel_title, (panel_x + 30, panel_y + 14))

    special_card_specs = [
        (2, pc.cards.DIAMONDS, "2"),
        (3, pc.cards.CLUBS, "3"),
        (4, pc.cards.HEARTS, "4"),
        (7, pc.cards.HEARTS, "7"),
        (8, pc.cards.SPADES, "8"),
        (10, pc.cards.DIAMONDS, "10"),
        (14, pc.cards.SPADES, "Joker"),
    ]
    card_label_font = pygame.font.SysFont("calibri", 24)
    card_width = 82
    card_height = 102
    panel_padding = 24
    available_width = panel_width - panel_padding * 2
    total_card_width = card_width * len(special_card_specs)
    card_gap = 0
    if len(special_card_specs) > 1 and available_width > total_card_width:
        card_gap = (available_width - total_card_width) // (
            len(special_card_specs) - 1
        )
    content_width = total_card_width + card_gap * (len(special_card_specs) - 1)
    start_x = panel_x + (panel_width - content_width) // 2
    for index, card_spec in enumerate(special_card_specs):
        num, shape, label = card_spec
        card_image = pc.load_scaled_image(
            pc.cards.CARDSIMAGES[(num, shape)],
            (card_width, card_height),
            pc.PINK,
        )
        draw_x = start_x + index * (card_width + card_gap)
        draw_y = panel_y + 50
        pc.screen.blit(card_image, (draw_x, draw_y))
        label_text = card_label_font.render(label, 1, pc.BLACK)
        label_x = draw_x + (card_width - label_text.get_width()) // 2
        pc.screen.blit(label_text, (label_x, draw_y + card_height + 8))

    top_mask_rect = pygame.Rect(0, 0, pc.WINDOW_WIDTH, content_top)
    pygame.draw.rect(pc.screen, pc.LIGHT_GREY, top_mask_rect)

    back_rect = draw_page_top_bar(
        "Official Rules", header_height, "Scroll to see more"
    )

    back = False
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == pc.LEFT:
        if back_rect.collidepoint(pos):
            back = True

    if back:
        RULES_SCROLL_OFFSET = 0
        return return_screen
    return "RULES"


def draw_settings_top_bar(header_height: int = 140) -> None:
    draw_page_top_bar("Quick Game Settings", header_height)


def settings_menu(event: pygame.event.Event, pos: MousePos) -> ScreenState:
    global SETTINGS_HOST_INPUT, SETTINGS_PORT_INPUT
    global SETTINGS_ACTIVE_FIELD, SETTINGS_STATUS_TEXT

    pc = get_client_module()

    if SETTINGS_HOST_INPUT is None or SETTINGS_PORT_INPUT is None:
        saved_host, saved_port = pc.read_server_preferences()
        SETTINGS_HOST_INPUT = saved_host
        SETTINGS_PORT_INPUT = str(saved_port)

    img = pc.load_image(pc.BACKGROUND)
    pc.screen.blit(img, (0, 0))

    header_height = 140
    draw_settings_top_bar(header_height)

    body_title_y = header_height + 30
    controls_center_y = pc.WINDOW_HEIGHT / 2 + 65

    quick_game_settings = pc.button.Button(
        pc.PINK,
        pc.WINDOW_WIDTH / 2 - 350,
        body_title_y,
        700,
        100,
        "Quick Game Settings",
    )
    number_of_players = pc.button.Button(
        pc.WHITE,
        pc.WINDOW_WIDTH / 2 - 350,
        body_title_y + 125,
        700,
        100,
        "Number Of Players",
    )

    minus_button = pc.button.Button(
        pc.WHITE,
        pc.WINDOW_WIDTH / 2 - 110 - 50 - 170,
        controls_center_y - 50,
        120,
        100,
        "-",
    )

    num = pc.read_preferences_count()

    number = pc.button.Button(
        pc.WHITE,
        pc.WINDOW_WIDTH / 2 - 50,
        controls_center_y - 50,
        100,
        100,
        str(num),
    )

    plus_button = pc.button.Button(
        pc.WHITE,
        pc.WINDOW_WIDTH / 2 + 110 + 50,
        controls_center_y - 50,
        120,
        100,
        "+",
    )

    back = False
    back_rect = pygame.Rect(25, 26, 210, 72)

    connection_settings = pc.button.Button(
        pc.PINK,
        pc.WINDOW_WIDTH / 2 - 350,
        controls_center_y + 105,
        700,
        100,
        "Connection Settings",
    )

    host_label = pc.button.Button(
        pc.WHITE,
        pc.WINDOW_WIDTH / 2 - 350,
        controls_center_y + 230,
        320,
        80,
        "Server Host",
    )
    host_input_rect = pygame.Rect(
        int(pc.WINDOW_WIDTH / 2 - 10),
        int(controls_center_y + 230),
        360,
        80,
    )

    port_label = pc.button.Button(
        pc.WHITE,
        pc.WINDOW_WIDTH / 2 - 350,
        controls_center_y + 330,
        320,
        80,
        "Server Port",
    )
    port_input_rect = pygame.Rect(
        int(pc.WINDOW_WIDTH / 2 - 10),
        int(controls_center_y + 330),
        360,
        80,
    )

    save_button = pc.button.Button(
        pc.WHITE,
        pc.WINDOW_WIDTH / 2 - 350,
        controls_center_y + 440,
        700,
        90,
        "Save Connection",
        font_size=46,
    )

    pc.red_raw_window(quick_game_settings)
    pc.red_raw_window(number_of_players)
    pc.red_raw_window(minus_button)
    pc.red_raw_window(number)
    pc.red_raw_window(plus_button)
    pc.red_raw_window(connection_settings)
    pc.red_raw_window(host_label)
    pc.red_raw_window(port_label)
    pc.red_raw_window(save_button)

    input_font = pygame.font.SysFont("calibri", 40)
    status_font = pygame.font.SysFont("calibri", 32)

    host_outline = pc.PINK if SETTINGS_ACTIVE_FIELD == "host" else pc.BLACK
    port_outline = pc.PINK if SETTINGS_ACTIVE_FIELD == "port" else pc.BLACK

    pygame.draw.rect(pc.screen, pc.WHITE, host_input_rect, 0)
    pygame.draw.rect(pc.screen, host_outline, host_input_rect, 3)
    host_text = input_font.render(SETTINGS_HOST_INPUT, 1, pc.BLACK)
    pc.screen.blit(
        host_text,
        (host_input_rect.x + 10, host_input_rect.y + 20),
    )

    pygame.draw.rect(pc.screen, pc.WHITE, port_input_rect, 0)
    pygame.draw.rect(pc.screen, port_outline, port_input_rect, 3)
    port_text = input_font.render(SETTINGS_PORT_INPUT, 1, pc.BLACK)
    pc.screen.blit(
        port_text,
        (port_input_rect.x + 10, port_input_rect.y + 20),
    )

    if SETTINGS_STATUS_TEXT:
        status_text = status_font.render(SETTINGS_STATUS_TEXT, 1, pc.BLACK)
        pc.screen.blit(
            status_text,
            (
                pc.WINDOW_WIDTH / 2 - status_text.get_width() / 2,
                controls_center_y + 545,
            ),
        )

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == pc.LEFT:
        if minus_button.is_over(pos):
            if num > 2:
                num -= 1
                pc.write_preferences_count(num)

        elif plus_button.is_over(pos):
            if num < 4:
                num += 1
                pc.write_preferences_count(num)

        elif host_input_rect.collidepoint(pos):
            SETTINGS_ACTIVE_FIELD = "host"

        elif port_input_rect.collidepoint(pos):
            SETTINGS_ACTIVE_FIELD = "port"

        elif save_button.is_over(pos):
            host = SETTINGS_HOST_INPUT.strip()
            try:
                port = int(SETTINGS_PORT_INPUT)
                if not host:
                    raise ValueError
                pc.write_server_preferences(host, port)
                SETTINGS_STATUS_TEXT = "Connection saved"
            except (TypeError, ValueError):
                SETTINGS_STATUS_TEXT = "Enter a valid host and port"

        elif back_rect.collidepoint(pos):
            back = True

        else:
            SETTINGS_ACTIVE_FIELD = None

    elif event.type == pygame.KEYDOWN:
        if SETTINGS_ACTIVE_FIELD == "host":
            if event.key == pygame.K_BACKSPACE:
                SETTINGS_HOST_INPUT = SETTINGS_HOST_INPUT[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                SETTINGS_ACTIVE_FIELD = "port"
            elif event.unicode and event.unicode.isprintable():
                if event.unicode != " " and len(SETTINGS_HOST_INPUT) < 64:
                    SETTINGS_HOST_INPUT += event.unicode
        elif SETTINGS_ACTIVE_FIELD == "port":
            if event.key == pygame.K_BACKSPACE:
                SETTINGS_PORT_INPUT = SETTINGS_PORT_INPUT[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                host = SETTINGS_HOST_INPUT.strip()
                try:
                    port = int(SETTINGS_PORT_INPUT)
                    if not host:
                        raise ValueError
                    pc.write_server_preferences(host, port)
                    SETTINGS_STATUS_TEXT = "Connection saved"
                    SETTINGS_ACTIVE_FIELD = None
                except (TypeError, ValueError):
                    SETTINGS_STATUS_TEXT = "Enter a valid host and port"
            elif event.unicode.isdigit() and len(SETTINGS_PORT_INPUT) < 5:
                SETTINGS_PORT_INPUT += event.unicode

    if event.type == pygame.MOUSEMOTION:
        minus_button.color = (
            pc.LIGHT_GREY if minus_button.is_over(pos) else pc.WHITE
        )
        plus_button.color = (
            pc.LIGHT_GREY if plus_button.is_over(pos) else pc.WHITE
        )
        save_button.color = (
            pc.LIGHT_GREY if save_button.is_over(pos) else pc.WHITE
        )

    if back:
        return "OPEN_SCREEN"
    else:
        return "SETTINGS"


def create_a_room_menu(
    event: pygame.event.Event, pos: MousePos, num: int
) -> ScreenState:
    pc = get_client_module()

    img = pc.load_image(pc.BACKGROUND)
    pc.screen.blit(img, (0, 0))

    create_a_room_button = pc.button.Button(
        pc.PINK,
        pc.WINDOW_WIDTH / 2 - 350,
        75,
        700,
        100,
        "Create A Room",
    )

    minus = pc.load_image(pc.MOVE_LEFT, pc.PINK)
    pc.screen.blit(
        minus,
        (pc.WINDOW_WIDTH / 2 - 110 - 50 - 220, pc.WINDOW_HEIGHT / 2 - 115),
    )

    number = pc.button.Button(
        pc.WHITE,
        pc.WINDOW_WIDTH / 2 - 50,
        pc.WINDOW_HEIGHT / 2 - 50,
        100,
        100,
        str(num),
    )

    plus = pc.load_image(pc.MOVE_RIGHT, pc.PINK)
    pc.screen.blit(
        plus, (pc.WINDOW_WIDTH / 2 + 110 + 50, pc.WINDOW_HEIGHT / 2 - 115)
    )

    create = pc.button.Button(
        pc.WHITE,
        pc.WINDOW_WIDTH / 2 - 350,
        pc.WINDOW_HEIGHT - 150,
        700,
        100,
        "Create",
    )

    back_button = pc.load_image(pc.ICON, pc.PINK)
    pc.screen.blit(back_button, (25, 25))

    back = False
    do_create = False

    pc.red_raw_window(create_a_room_button)
    pc.red_raw_window(number)
    pc.red_raw_window(create)

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == pc.LEFT:
        if create.is_over(pos):
            do_create = True

        elif (
            pc.WINDOW_WIDTH / 2 - 110 - 50 - 220
            < pos[0]
            < pc.WINDOW_WIDTH / 2 - 110 - 50
        ):
            if (
                pc.WINDOW_HEIGHT / 2 - 115
                < pos[1]
                < pc.WINDOW_HEIGHT / 2 - 115 + 230
            ):
                if num > 2:
                    num -= 1

        elif (
            pc.WINDOW_WIDTH / 2 + 110 + 50
            < pos[0]
            < pc.WINDOW_WIDTH / 2 + 110 + 50 + 220
        ):
            if (
                pc.WINDOW_HEIGHT / 2 - 115
                < pos[1]
                < pc.WINDOW_HEIGHT / 2 - 115 + 230
            ):
                if num < 4:
                    num += 1

        elif 25 < pos[0] < 25 + 250:
            if 25 < pos[1] < 25 + 250:
                back = True

    if event.type == pygame.MOUSEMOTION:
        if create.is_over(pos):
            create.color = pc.LIGHT_GREY
        else:
            create.color = pc.WHITE

    if do_create:
        pc.SEND.append("SCREEN~CREATE_A_ROOM" + "~" + str(num) + "~~~")
    if back:
        return "OPEN_SCREEN"
    else:
        return "CREATE_A_ROOM", num


def wait_to_full(
    event: pygame.event.Event,
    pos: MousePos,
    room: int,
    p_now: int,
    people: int,
) -> ScreenState:
    pc = get_client_module()

    cancel_button = pc.button.Button(
        pc.WHITE,
        pc.WINDOW_WIDTH / 2 - 150,
        pc.WINDOW_HEIGHT - 130,
        300,
        80,
        "Cancel",
    )

    if not p_now == people:
        img = pc.load_image(pc.BACKGROUND)
        pc.screen.blit(img, (0, 0))

        rn = pc.button.Button(pc.PINK, 2, 2, 400, 100, "ROOM: " + str(room))

        pn = pc.button.Button(
            pc.WHITE,
            pc.WINDOW_WIDTH - 200 - 2,
            2,
            200,
            100,
            str(p_now) + "/" + str(people),
        )

        font = pygame.font.SysFont("algerian", 80)
        text = font.render("waiting for the room to be full...", 1, pc.WHITE)
        pc.screen.blit(
            text,
            (
                pc.WINDOW_WIDTH / 2 - text.get_width() / 2,
                pc.WINDOW_HEIGHT / 2 - text.get_height() / 2,
            ),
        )

        pc.red_raw_window(rn)
        pc.red_raw_window(pn)
        pc.red_raw_window(cancel_button)

    cancel = False
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == pc.LEFT:
        if cancel_button.is_over(pos):
            cancel = True

    if event.type == pygame.MOUSEMOTION:
        cancel_button.color = (
            pc.LIGHT_GREY if cancel_button.is_over(pos) else pc.WHITE
        )

    if cancel:
        pc.SEND.append("WAITING~CANCEL~~~")
        return "OPEN_SCREEN"

    return "WAITING", room, p_now, people


def finish(
    event: pygame.event.Event, pos: MousePos, reason: list[str]
) -> ScreenState:
    pc = get_client_module()

    img = pc.load_image(pc.BACKGROUND)
    pc.screen.blit(img, (0, 0))

    font = pygame.font.SysFont("algerian", 80)
    text = font.render(reason[0], 1, pc.WHITE)
    pc.screen.blit(
        text,
        (
            pc.WINDOW_WIDTH / 2 - text.get_width() / 2,
            pc.WINDOW_HEIGHT / 2 - text.get_height() / 2,
        ),
    )

    back_button = pc.load_image(pc.ICON, pc.PINK)
    pc.screen.blit(back_button, (25, 25))

    back = False

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == pc.LEFT:
        if 25 < pos[0] < 25 + 250:
            if 25 < pos[1] < 25 + 250:
                back = True

    if back:
        return "OPEN_SCREEN"
    else:
        return "FINISH", reason[0]
