import pygame

from typing import List, Tuple, Set

from .utils.colors import Colors
from .utils.screen_pos import ScreenPos
from ..model.pos import Pos


class TileEffectView(pygame.sprite.Sprite):
    def __init__(self, board_pos: Pos, screen_pos: ScreenPos, size: int):
        pygame.sprite.Sprite.__init__(self)

        self.board_pos = board_pos
        self.screen_pos = screen_pos
        self.size = size

        self.image = pygame.Surface((size, size))
        self.image.fill(Colors.PURPLE.value)
        self.image.set_colorkey(Colors.PURPLE.value)
        self.image.set_alpha(50)

        self.rect = self.image.get_rect()
        self.rect.x = self.screen_pos.x
        self.rect.y = self.screen_pos.y

        self.background = pygame.Surface((size, size))
        self.background.fill(Colors.LIGHT_BLUE.value)
        self.background.set_alpha(0)

        self.background_rect = self.background.get_rect()
        self.background_rect.x = self.screen_pos.x
        self.background_rect.y = self.screen_pos.y

        self.hint_background = pygame.Surface((size, size))
        self.hint_background.set_alpha(0)

        self.hint_background_rect = self.hint_background.get_rect()
        self.hint_background_rect.x = self.screen_pos.x
        self.hint_background_rect.y = self.screen_pos.y
    
    def update(self, 
            mouse_screen_pos: ScreenPos, 
            legal_moves: List[Pos], 
            legal_captures: List[Pos], 
            positive_hints: Set[Pos], 
            negative_hints: Set[Pos], 
            last_move: Tuple[Pos, Pos]):

        self.image.fill(Colors.PURPLE.value)

        origin, dest = last_move
        if self.board_pos == origin or self.board_pos == dest:
            self.background.set_alpha(128)
        else:
            self.background.set_alpha(0)

        if self.board_pos in positive_hints:
            self.hint_background.fill(Colors.GREEN.value)
            self.hint_background.set_alpha(128)
        elif self.board_pos in negative_hints:
            self.hint_background.fill(Colors.RED.value)
            self.hint_background.set_alpha(128)
        else:
            self.hint_background.set_alpha(0)
        
        if self.board_pos in legal_captures:
            pygame.draw.circle(self.image, Colors.BLACK.value, \
                (self.size//2, self.size//2), self.size//2, width=self.size//10)

        if self.board_pos in legal_moves:
            pygame.draw.circle(self.image, Colors.BLACK.value, \
                (self.size//2, self.size//2), self.size//6, width=0)

        if self.rect.collidepoint((mouse_screen_pos[0], mouse_screen_pos[1])):
            color = Colors.CREAM.value if self.board_pos[0] % 2 == self.board_pos[1] % 2 else Colors.BLUE.value
            pygame.draw.rect(self.image, color, [0, 0, self.size, self.size], self.size//10)
