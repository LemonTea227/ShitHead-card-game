from typing import TypeAlias

import pygame

MousePos: TypeAlias = tuple[float, float]
ScreenState: TypeAlias = str | tuple[object, ...]


def choose_a_room_menu(
    event: pygame.event.Event,
    pos: MousePos,
    games_message: list[str],
    page: int,
) -> ScreenState:
    from pages import gameplay_pages

    return gameplay_pages.choose_a_room_menu(event, pos, games_message, page)
