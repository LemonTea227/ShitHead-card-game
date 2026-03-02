import pygame
from typing import Optional

PINK = (255, 20, 147)


class Button:
    _fonts: dict[int, pygame.font.Font] = {}

    def __init__(
        self,
        color: tuple[int, int, int],
        x: float,
        y: float,
        width: float,
        height: float,
        text: str = "",
        text_color: tuple[int, int, int] = (0, 0, 0),
        font_size: int = 60,
    ) -> None:
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.text_color = text_color
        self.font_size = font_size

    def draw(
        self,
        win: pygame.Surface,
        outline: Optional[tuple[int, int, int]] = None,
    ) -> None:
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(
                win,
                outline,
                (self.x - 2, self.y - 2, self.width + 4, self.height + 4),
                0,
            )

        pygame.draw.rect(
            win, self.color, (self.x, self.y, self.width, self.height), 0
        )

        if self.text != "":
            if self.font_size not in Button._fonts:
                Button._fonts[self.font_size] = pygame.font.SysFont(
                    "calibri", self.font_size
                )
            text = Button._fonts[self.font_size].render(
                self.text, 1, self.text_color
            )
            win.blit(
                text,
                (
                    self.x + (self.width // 2 - text.get_width() // 2),
                    self.y + (self.height // 2 - text.get_height() // 2),
                ),
            )

    def is_over(self, pos: tuple[float, float]) -> bool:
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True

        return False
