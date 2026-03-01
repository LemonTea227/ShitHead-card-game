import pygame

PINK = (255, 20, 147)


class Button:
    _font = None

    def __init__(
        self, color, x, y, width, height, text="", text_color=(0, 0, 0)
    ):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.text_color = text_color

    def draw(self, win, outline=None):
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
            if Button._font is None:
                Button._font = pygame.font.SysFont("calibri", 60)
            text = Button._font.render(self.text, 1, self.text_color)
            win.blit(
                text,
                (
                    self.x + (self.width // 2 - text.get_width() // 2),
                    self.y + (self.height // 2 - text.get_height() // 2),
                ),
            )

    def is_over(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True

        return False
