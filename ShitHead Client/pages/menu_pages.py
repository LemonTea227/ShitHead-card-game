import pygame
from typing import Optional, TypeAlias

from pages._client_ref import get_client_module

MousePos: TypeAlias = tuple[float, float]
ScreenState: TypeAlias = str | tuple[object, ...]
RULES_SCROLL_OFFSET = 0


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

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == pc.LEFT:
        if quick_game.is_over(pos):
            next_screen = "QUICK_GAME"

        elif choose_a_room.is_over(pos):
            next_screen = "CHOOSE_A_ROOM"

        elif create_a_room.is_over(pos):
            next_screen = "CREATE_A_ROOM"

        elif rules.is_over(pos):
            next_screen = "RULES"

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

    scrn: ScreenState = "OPEN_SCREEN"
    if next_screen == "QUICK_GAME":
        preferences = str(pc.read_preferences_count())
        pc.SEND.append(str(next_screen) + "~" + str(preferences) + "~~~")
    elif next_screen == "CHOOSE_A_ROOM":
        pc.SEND.append("SCREEN~CHOOSE_A_ROOM~~~")
        scrn = "OPEN_SCREEN"
    elif next_screen == "CREATE_A_ROOM":
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
    min_scroll_offset = -380
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
            "The rest of the deck stays in the center as the draw deck.",
            "The throw deck begins empty.",
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
        430 + y_shift,
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
        700 + y_shift,
        1580,
        320,
        "Special Cards",
        [
            "2: Reset card, can be played freely.",
            "3: Transparent card, follows the previous card rule.",
            "4: Cut-in card, can be thrown out of turn when pile is empty.",
            "7: Next play must be 7 or lower (or special cards that bypass).",
            "8: Skip next player.",
            "10: Burn the throw deck.",
            "Joker (14): Give throw deck to selected player "
            "(or previous player by default).",
        ],
        text_max_width=1200,
    )

    pygame.draw.rect(pc.screen, pc.WHITE, (760, 1060 + y_shift, 900, 220), 0)
    pygame.draw.rect(pc.screen, pc.BLACK, (760, 1060 + y_shift, 900, 220), 2)
    panel_title_font = pygame.font.SysFont("calibri", 30)
    panel_title = panel_title_font.render(
        "Special cards shown in-game", 1, pc.PINK
    )
    pc.screen.blit(panel_title, (790, 1074 + y_shift))

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
    start_x = 825
    for index, card_spec in enumerate(special_card_specs):
        num, shape, label = card_spec
        card_image = pc.load_scaled_image(
            pc.cards.CARDSIMAGES[(num, shape)], (82, 102), pc.PINK
        )
        draw_x = start_x + index * 130
        draw_y = 1110 + y_shift
        pc.screen.blit(card_image, (draw_x, draw_y))
        label_text = card_label_font.render(label, 1, pc.BLACK)
        pc.screen.blit(label_text, (draw_x + 18, draw_y + 112))

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
    pc = get_client_module()

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
    pc.red_raw_window(quick_game_settings)
    pc.red_raw_window(number_of_players)
    pc.red_raw_window(minus_button)
    pc.red_raw_window(number)
    pc.red_raw_window(plus_button)

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == pc.LEFT:
        if minus_button.is_over(pos):
            if num > 2:
                num -= 1
                pc.write_preferences_count(num)

        elif plus_button.is_over(pos):
            if num < 4:
                num += 1
                pc.write_preferences_count(num)

        elif back_rect.collidepoint(pos):
            back = True

    if event.type == pygame.MOUSEMOTION:
        minus_button.color = (
            pc.LIGHT_GREY if minus_button.is_over(pos) else pc.WHITE
        )
        plus_button.color = (
            pc.LIGHT_GREY if plus_button.is_over(pos) else pc.WHITE
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
