import pygame

from pages._client_ref import get_client_module


def draw_wrapped_lines(font, lines, x, y, max_width, color):
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


def draw_rules_section(x, y, width, height, title, lines, text_max_width=None):
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


def open_screen(event, pos):
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

    scrn = "OPEN_SCREEN"
    if next_screen == "QUICK_GAME":
        preferences = ""
        with open("preferences.txt", "r") as f:
            preferences += f.read()
        pc.SEND.append(str(next_screen) + "~" + str(preferences) + "~~~")
    elif next_screen == "CHOOSE_A_ROOM":
        pc.SEND.append("SCREEN~CHOOSE_A_ROOM~~~")
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


def rules_menu(event, pos):
    pc = get_client_module()

    img = pc.load_image(pc.BACKGROUND)
    pc.screen.blit(img, (0, 0))

    title_font = pygame.font.SysFont("algerian", 64)
    title = title_font.render("ShitHead - Official Rules", 1, pc.WHITE)
    pc.screen.blit(title, (pc.WINDOW_WIDTH / 2 - title.get_width() / 2, 30))

    back_button = pc.load_image(pc.ICON, pc.PINK)
    pc.screen.blit(back_button, (25, 25))

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

    pygame.draw.rect(pc.screen, pc.WHITE, (980, 720, 620, 180), 0)
    pygame.draw.rect(pc.screen, pc.BLACK, (980, 720, 620, 180), 2)
    panel_title_font = pygame.font.SysFont("calibri", 28)
    panel_title = panel_title_font.render(
        "Special cards shown in-game", 1, pc.PINK
    )
    pc.screen.blit(panel_title, (1000, 730))

    settings_small = pc.load_scaled_image(pc.SETTINGS, (90, 90), pc.PINK)
    move_left_small = pc.load_scaled_image(pc.MOVE_LEFT, (80, 80), pc.PINK)
    move_right_small = pc.load_scaled_image(pc.MOVE_RIGHT, (80, 80), pc.PINK)
    pc.screen.blit(settings_small, (740, 210))
    pc.screen.blit(move_left_small, (1220, 210))
    pc.screen.blit(move_right_small, (1315, 210))

    special_card_specs = [
        (2, pc.cards.DIAMONDS, "2"),
        (3, pc.cards.CLUBS, "3"),
        (4, pc.cards.HEARTS, "4"),
        (8, pc.cards.SPADES, "8"),
        (10, pc.cards.DIAMONDS, "10"),
        (14, pc.cards.SPADES, "Joker"),
    ]
    card_label_font = pygame.font.SysFont("calibri", 24)
    start_x = 1005
    for index, card_spec in enumerate(special_card_specs):
        num, shape, label = card_spec
        card_image = pc.load_scaled_image(
            pc.cards.CARDSIMAGES[(num, shape)], (82, 102), pc.PINK
        )
        draw_x = start_x + index * 98
        draw_y = 770
        pc.screen.blit(card_image, (draw_x, draw_y))
        label_text = card_label_font.render(label, 1, pc.BLACK)
        pc.screen.blit(label_text, (draw_x + 26, draw_y + 112))

    back = False
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == pc.LEFT:
        if 25 < pos[0] < 25 + 250 and 25 < pos[1] < 25 + 250:
            back = True

    if back:
        return "OPEN_SCREEN"
    return "RULES"


def settings_menu(event, pos):
    pc = get_client_module()

    img = pc.load_image(pc.BACKGROUND)
    pc.screen.blit(img, (0, 0))

    quick_game_settings = pc.button.Button(
        pc.PINK,
        pc.WINDOW_WIDTH / 2 - 350,
        75,
        700,
        100,
        "Quick Game Settings",
    )
    number_of_players = pc.button.Button(
        pc.WHITE,
        pc.WINDOW_WIDTH / 2 - 350,
        200,
        700,
        100,
        "Number Of Players",
    )

    minus = pc.load_image(pc.MOVE_LEFT, pc.PINK)
    pc.screen.blit(
        minus,
        (pc.WINDOW_WIDTH / 2 - 110 - 50 - 220, pc.WINDOW_HEIGHT / 2 - 115),
    )

    num = 0
    try:
        with open("preferences.txt", "r") as f:
            num = int(f.read())
    except IOError:
        num = 2

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

    back_button = pc.load_image(pc.ICON, pc.PINK)
    pc.screen.blit(back_button, (25, 25))

    back = False
    pc.red_raw_window(quick_game_settings)
    pc.red_raw_window(number_of_players)
    pc.red_raw_window(number)

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == pc.LEFT:
        if (
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
                    with open("preferences.txt", "w") as f:
                        f.write(str(num))

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
                    with open("preferences.txt", "w") as f:
                        f.write(str(num))

        elif 25 < pos[0] < 25 + 250:
            if 25 < pos[1] < 25 + 250:
                back = True

    if back:
        return "OPEN_SCREEN"
    else:
        return "SETTINGS"


def create_a_room_menu(event, pos, num):
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


def wait_to_full(event, pos, room, p_now, people):
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


def finish(event, pos, reason):
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
