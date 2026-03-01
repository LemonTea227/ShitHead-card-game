from typing import TypeAlias

import pygame

MousePos: TypeAlias = tuple[float, float]
ScreenState: TypeAlias = str | tuple[object, ...]


def rules_menu(
    event: pygame.event.Event,
    pos: MousePos,
    return_screen: str = "OPEN_SCREEN",
) -> ScreenState:
    from pages import menu_pages

    return menu_pages.rules_menu(event, pos, return_screen)
