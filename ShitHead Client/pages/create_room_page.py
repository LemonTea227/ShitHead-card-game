from typing import TypeAlias

import pygame

MousePos: TypeAlias = tuple[float, float]
ScreenState: TypeAlias = str | tuple[object, ...]


def create_a_room_menu(
    event: pygame.event.Event, pos: MousePos, num: int
) -> ScreenState:
    from pages import menu_pages

    return menu_pages.create_a_room_menu(event, pos, num)
