import pygame

import os

from.utils.colors import Colors
from .utils.screen_pos import ScreenPos
from ..model.player import Player
from ..model.pos import Pos


class PromotionView(pygame.sprite.Sprite):
    def __init__(self, 
                image_directory: str,
                sprite_size: int,
                board_offset: ScreenPos,
                player: Player):
        pygame.sprite.Sprite.__init__(self)

        self.image_directory = image_directory
        self.sprite_size = sprite_size
        self.board_offset = board_offset
        self.player = player

        self.images = []
        self.rects = []
        self.promotion_pieces = ["Q", "R", "N", "B"]
        for i, promotion_piece in enumerate(self.promotion_pieces):
            path_to_sprite = os.path.join(image_directory, f"{self.player.name}_{promotion_piece}.png")
            image = pygame.image.load(path_to_sprite).convert_alpha()
            image = pygame.transform.smoothscale(image, (sprite_size, sprite_size))
            self.images.append(image)

            rect = image.get_rect()
            rect.x = 0
            rect.y = i*sprite_size
            self.rects.append(rect)

        path_to_sprite = os.path.join(image_directory, "CANCEL.png")
        image = pygame.image.load(path_to_sprite).convert_alpha()
        image = pygame.transform.smoothscale(image, (sprite_size, sprite_size))
        self.images.append(image)
        rect = image.get_rect()
        rect.x = 0
        rect.y = i*sprite_size
        self.rects.append(rect)

        self.background = pygame.Surface((sprite_size, 5*sprite_size))
        self.background.fill(Colors.WHITE.value)
        pygame.draw.rect(self.background, Colors.BLACK.value, [0, 0, sprite_size, 5*sprite_size], sprite_size//20)
        self.background.set_alpha(255)

        self.background_rect = self.background.get_rect()
        self.background_rect.x = 0
        self.background_rect.y = 0

    def update(self, possible_promotion: Pos, for_player: Player):
        if possible_promotion is None:
            self.background.set_alpha(0)
        elif for_player is not None and for_player == self.player:
            # Make panel visible 
            self.background.set_alpha(255)

            if possible_promotion.rank == 0:
                self.background_rect.y = self.board_offset.y + 3*self.sprite_size
            else:
                self.background_rect.y = self.board_offset.y
            self.background_rect.x = self.board_offset.x + int(possible_promotion.file * self.sprite_size)

            for i in range(len(self.rects)):
                self.rects[i].x = self.background_rect.x
                self.rects[i].y = self.background_rect.y + i*self.sprite_size
        else:
            self.background.set_alpha(0)
    
    def click(self, mouse_screen_pos: ScreenPos) -> str:
        for i in range(len(self.rects)):
            rect = self.rects[i]
            if rect.collidepoint((mouse_screen_pos[0], mouse_screen_pos[1])):
                if i >= len(self.promotion_pieces):
                    return None
                else:
                    return self.promotion_pieces[i]
        return None

