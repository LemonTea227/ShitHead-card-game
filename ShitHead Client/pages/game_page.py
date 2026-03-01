from typing import TypeAlias

import pygame

MousePos: TypeAlias = tuple[float, float]
ScreenState: TypeAlias = str | tuple[object, ...]


def game_manager(
    event: pygame.event.Event,
    pos: MousePos,
    cards_message: list[str],
    cards_to_throw: list[object],
    to_who: int,
) -> ScreenState:
    from pages import gameplay_pages

    return gameplay_pages.game_manager(
        event, pos, cards_message, cards_to_throw, to_who
    )
