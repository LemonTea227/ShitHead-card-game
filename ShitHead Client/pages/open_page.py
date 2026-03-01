from typing import TypeAlias

import pygame

MousePos: TypeAlias = tuple[float, float]
ScreenState: TypeAlias = str | tuple[object, ...]


def open_screen(event: pygame.event.Event, pos: MousePos) -> ScreenState:
    from pages import menu_pages

    return menu_pages.open_screen(event, pos)
