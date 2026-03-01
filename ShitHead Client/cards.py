import pygame
from typing import Tuple

PINK = (255, 20, 147)
DIAMONDS = 1
CLUBS = 2
HEARTS = 3
SPADES = 4
# https://en.wikipedia.org/wiki/Standard_52-card_deck
CARDSIMAGES = {
    (1, 1): "proj_pics/ace_of_diamonds.png",
    (2, 1): "proj_pics/two_of_diamonds.png",
    (3, 1): "proj_pics/three_of_diamonds.png",
    (4, 1): "proj_pics/four_of_diamonds.png",
    (5, 1): "proj_pics/five_of_diamonds.png",
    (6, 1): "proj_pics/six_of_diamonds.png",
    (7, 1): "proj_pics/seven_of_diamonds.png",
    (8, 1): "proj_pics/eight_of_diamonds.png",
    (9, 1): "proj_pics/nine_of_diamonds.png",
    (10, 1): "proj_pics/ten_of_diamonds.png",
    (11, 1): "proj_pics/jack_of_diamonds.png",
    (12, 1): "proj_pics/queen_of_diamonds.png",
    (13, 1): "proj_pics/king_of_diamonds.png",
    (14, 1): "proj_pics/red_joker.png",
    (1, 2): "proj_pics/ace_of_clubs.png",
    (2, 2): "proj_pics/two_of_clubs.png",
    (3, 2): "proj_pics/three_of_clubs.png",
    (4, 2): "proj_pics/four_of_clubs.png",
    (5, 2): "proj_pics/five_of_clubs.png",
    (6, 2): "proj_pics/six_of_clubs.png",
    (7, 2): "proj_pics/seven_of_clubs.png",
    (8, 2): "proj_pics/eight_of_clubs.png",
    (9, 2): "proj_pics/nine_of_clubs.png",
    (10, 2): "proj_pics/ten_of_clubs.png",
    (11, 2): "proj_pics/jack_of_clubs.png",
    (12, 2): "proj_pics/queen_of_clubs.png",
    (13, 2): "proj_pics/king_of_clubs.png",
    (1, 3): "proj_pics/ace_of_hearts.png",
    (2, 3): "proj_pics/two_of_hearts.png",
    (3, 3): "proj_pics/three_of_hearts.png",
    (4, 3): "proj_pics/four_of_hearts.png",
    (5, 3): "proj_pics/five_of_hearts.png",
    (6, 3): "proj_pics/six_of_hearts.png",
    (7, 3): "proj_pics/seven_of_hearts.png",
    (8, 3): "proj_pics/eight_of_hearts.png",
    (9, 3): "proj_pics/nine_of_hearts.png",
    (10, 3): "proj_pics/ten_of_hearts.png",
    (11, 3): "proj_pics/jack_of_hearts.png",
    (12, 3): "proj_pics/queen_of_hearts.png",
    (13, 3): "proj_pics/king_of_hearts.png",
    (1, 4): "proj_pics/ace_of_spades.png",
    (2, 4): "proj_pics/two_of_spades.png",
    (3, 4): "proj_pics/three_of_spades.png",
    (4, 4): "proj_pics/four_of_spades.png",
    (5, 4): "proj_pics/five_of_spades.png",
    (6, 4): "proj_pics/six_of_spades.png",
    (7, 4): "proj_pics/seven_of_spades.png",
    (8, 4): "proj_pics/eight_of_spades.png",
    (9, 4): "proj_pics/nine_of_spades.png",
    (10, 4): "proj_pics/ten_of_spades.png",
    (11, 4): "proj_pics/jack_of_spades.png",
    (12, 4): "proj_pics/queen_of_spades.png",
    (13, 4): "proj_pics/king_of_spades.png",
    (14, 4): "proj_pics/black_joker.png",
    (None, None): "proj_pics/back_card.png",
}
IMAGE_CACHE = {}


def load_image(path: str) -> pygame.Surface:
    image = IMAGE_CACHE.get(path)
    if image is None:
        image = pygame.image.load(path).convert()
        image.set_colorkey(PINK)
        IMAGE_CACHE[path] = image
    return image


class Cards(pygame.sprite.Sprite):
    def __init__(
        self,
        number: int | None,
        shape: int | None,
        x: float,
        y: float,
    ) -> None:
        self.__shape = None
        self.__number = None
        self.__number = number
        self.__shape = shape
        self.x = x
        self.y = y
        self.__image = load_image(CARDSIMAGES[(self.__number, self.__shape)])
        self.__special = number in (2, 3, 4, 7, 8, 10, 14)

    def draw(self, win: pygame.Surface) -> None:
        win.blit(self.__image, (self.x, self.y))

    def get_number(self) -> int | None:
        return self.__number

    def get_shape(self) -> int | None:
        return self.__shape

    def is_over(self, pos: Tuple[float, float]) -> bool:
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if self.x < pos[0] < self.x + 200:
            if self.y < pos[1] < self.y + 250:
                return True

        return False
