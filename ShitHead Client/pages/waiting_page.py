from typing import TypeAlias

import pygame

MousePos: TypeAlias = tuple[float, float]
ScreenState: TypeAlias = str | tuple[object, ...]


def wait_to_full(
    event: pygame.event.Event,
    pos: MousePos,
    room: int,
    p_now: int,
    people: int,
) -> ScreenState:
    from pages import menu_pages

    return menu_pages.wait_to_full(event, pos, room, p_now, people)
