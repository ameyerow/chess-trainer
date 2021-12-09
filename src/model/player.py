from enum import Enum


class Player(Enum):
    WHITE = 0
    BLACK = 1

    def flip(self):
        if self == Player.WHITE:
            return Player.BLACK
        else:
            return Player.WHITE