import pygame

from typing import Set

import os
from .utils.colors import Colors
from .utils.screen_pos import ScreenPos
from ..model.pieces.piece import Piece
from ..model.pos import Pos

class PieceView(pygame.sprite.Sprite):
    def __init__(self, 
                image_directory: str, 
                piece_model: Piece,
                resting_screen_pos: ScreenPos,
                sprite_size: int):
        pygame.sprite.Sprite.__init__(self)
        self.piece_model = piece_model
        self.resting_screen_pos = resting_screen_pos
        self.selected = False
        self.resting = True

        path_to_sprite = os.path.join(image_directory, f"{self.piece_model.player.name}_{self.piece_model.name}.png")
        self.image = pygame.image.load(path_to_sprite).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (sprite_size, sprite_size))

        self.background = pygame.Surface((sprite_size, sprite_size))
        self.background.fill(Colors.LIGHT_BLUE.value)
        self.background.set_alpha(0)

        self.background_rect = self.background.get_rect()
        self.background_rect.x = self.resting_screen_pos.x
        self.background_rect.y = self.resting_screen_pos.y

        self.rect = self.image.get_rect()
        self.rect.x = self.resting_screen_pos.x
        self.rect.y = self.resting_screen_pos.y

    def update(self, pos: ScreenPos, positive_hints: Set[Pos], negative_hints: Set[Pos]):
        if self.resting:
            self.rect.x = self.resting_screen_pos.x
            self.rect.y = self.resting_screen_pos.y
        else:
            self.rect.centerx = pos.x
            self.rect.centery = pos.y

        if self.selected and self.piece_model.pos not in positive_hints and self.piece_model.pos not in negative_hints:
            self.background.set_alpha(128)
        else:
            self.background.set_alpha(0)
