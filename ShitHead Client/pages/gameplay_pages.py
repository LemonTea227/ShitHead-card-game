import pygame
from typing import TypeAlias

from pages._client_ref import get_client_module

MousePos: TypeAlias = tuple[float, float]
ScreenState: TypeAlias = str | tuple[object, ...]


def choose_a_room_menu(
    event: pygame.event.Event,
    pos: MousePos,
    games_message: list[str],
    page: int,
) -> ScreenState:
    pc = get_client_module()

    game = pc.game
    button = pc.button
    load_image = pc.load_image
    red_raw_window = pc.red_raw_window
    join_game = pc.join_game

    PINK = pc.PINK
    WHITE = pc.WHITE
    WINDOW_WIDTH = pc.WINDOW_WIDTH
    WINDOW_HEIGHT = pc.WINDOW_HEIGHT
    MOVE_LEFT = pc.MOVE_LEFT
    MOVE_RIGHT = pc.MOVE_RIGHT
    ICON = pc.ICON
    LIGHT_GREY = pc.LIGHT_GREY
    LEFT = pc.LEFT

    screen = pc.screen
    games = []
    for g in games_message:
        info = g.split(",")
        if len(info) == 3:
            room = game.Game(int(info[0]), int(info[2]), int(info[1]))
            games.append(room)

    img = load_image(pc.BACKGROUND)
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


def game_manager(
    event: pygame.event.Event,
    pos: MousePos,
    cards_message: list[str],
    cards_to_throw: list[object],
    to_who: int,
) -> ScreenState:
    pc = get_client_module()
    cards = pc.cards
    button = pc.button
    load_image = pc.load_image
    red_raw_window = pc.red_raw_window
    card_to_window = pc.card_to_window

    BACKGROUND = pc.BACKGROUND
    SETTINGS = pc.SETTINGS
    WINDOW_WIDTH = pc.WINDOW_WIDTH
    WINDOW_HEIGHT = pc.WINDOW_HEIGHT
    WHITE = pc.WHITE
    RED = pc.RED
    PINK = pc.PINK
    LEFT = pc.LEFT
    RIGHT = pc.RIGHT

    screen = pc.screen

    img = load_image(BACKGROUND)
    screen.blit(img, (0, 0))  # (left, top)
    pygame.display.flip()

    rules_icon_x = WINDOW_WIDTH - 150
    rules_icon_y = 22
    rules_icon = load_image(SETTINGS, PINK)
    screen.blit(rules_icon, (rules_icon_x, rules_icon_y))
    rules_label = button.Button(
        WHITE,
        rules_icon_x - 10,
        rules_icon_y + 125,
        148,
        52,
        "Rules",
    )
    red_raw_window(rules_label)
    rules_hitbox = pygame.Rect(rules_icon_x, rules_icon_y, 128, 128)

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
        if rules_hitbox.collidepoint(pos) or rules_label.is_over(pos):
            return "RULES_GAME", cards_message, cards_to_throw, to_who
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
        pc.SEND.append(message)
        return "GAME", cards_message, [], 0
    return "GAME", cards_message, cards_to_throw, to_who
