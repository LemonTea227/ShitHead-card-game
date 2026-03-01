from typing import TypeAlias

import pygame

MousePos: TypeAlias = tuple[float, float]
ScreenState: TypeAlias = str | tuple[object, ...]


def finish(
    event: pygame.event.Event, pos: MousePos, reason: list[str]
) -> ScreenState:
    from pages import menu_pages

    return menu_pages.finish(event, pos, reason)
