from typing import Tuple
import pygame
pygame.init()

import os
from .model.board import Board
from .model.pos import Pos
from enum import Enum

class Colors(Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    CREAM = (234, 233, 210)
    BLUE = (75, 115, 153)
    LIGHT_BLUE = (51, 191, 255)
    PURPLE = (255, 0, 255)

class PieceView(pygame.sprite.Sprite):
    def __init__(self, directory, piece, player, idx, rest_pos, size):
        """
        """
        pygame.sprite.Sprite.__init__(self)

        self.piece = piece
        self.player = player
        self.idx = idx
        self.rest_pos = rest_pos
        self.selected = False
        self.resting = True
        self.size = size

        path_to_sprite = os.path.join(directory, f"{self.player.name}_{self.piece.name}.png")
        self.image = pygame.image.load(path_to_sprite).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (size, size))

        self.background = pygame.Surface((size, size))
        self.background.fill(Colors.LIGHT_BLUE.value)
        self.background.set_alpha(0)

        self.background_rect = self.background.get_rect()
        self.background_rect.x = self.rest_pos[0]
        self.background_rect.y = self.rest_pos[1]

        self.rect = self.image.get_rect()
        self.rect.x = self.rest_pos[0]
        self.rect.y = self.rest_pos[1]
    
    def update(self, pos):
        if self.resting:
            self.rect.x = self.rest_pos[0]
            self.rect.y = self.rest_pos[1]
        else:
            self.rect.centerx = pos[0]
            self.rect.centery = pos[1]

        if self.selected:
            self.background.set_alpha(128)
        else:
            self.background.set_alpha(0)


class PieceGroup(pygame.sprite.Group):
    def by_resting(self, sprite):
        return not sprite.resting
    
    def draw(self, surface):
        sprites = self.sprites()
        surface_blit = surface.blit

        for sprite in sorted(sprites, key=self.by_resting):
            surface_blit(sprite.background, sprite.background_rect)
            self.spritedict[sprite] = surface_blit(sprite.image, sprite.rect)
        self.lostsprites = []

class TileEffectView(pygame.sprite.Sprite):
    def __init__(self, board_pos: Pos, screen_pos: Tuple[int, int], size: int):
        pygame.sprite.Sprite.__init__(self)

        self.board_pos = board_pos
        self.screen_pos = screen_pos
        self.size = size

        self.image = pygame.Surface((size, size))
        self.image.fill(Colors.PURPLE.value)
        self.image.set_colorkey(Colors.PURPLE.value)
        self.image.set_alpha(50)

        self.rect = self.image.get_rect()
        self.rect.x = self.screen_pos[0]
        self.rect.y = self.screen_pos[1]

        self.background = pygame.Surface((size, size))
        self.background.fill(Colors.LIGHT_BLUE.value)
        self.background.set_alpha(0)

        self.background_rect = self.background.get_rect()
        self.background_rect.x = self.screen_pos[0]
        self.background_rect.y = self.screen_pos[1]
    
    def update(self, pos, legal_moves, legal_captures, last_move):
        self.image.fill(Colors.PURPLE.value)

        origin, dest = last_move
        if self.board_pos == origin or self.board_pos == dest:
            self.background.set_alpha(128)
        else:
            self.background.set_alpha(0)
        
        if self.board_pos in legal_captures:
            pygame.draw.circle(self.image, Colors.BLACK.value, \
                (self.size//2, self.size//2), self.size//2, width=self.size//10)

        if self.board_pos in legal_moves:
            pygame.draw.circle(self.image, Colors.BLACK.value, \
                (self.size//2, self.size//2), self.size//6, width=0)

        if self.rect.collidepoint(pos):
            color = Colors.CREAM.value if self.board_pos[0] % 2 == self.board_pos[1] % 2 else Colors.BLUE.value
            pygame.draw.rect(self.image, color, [0, 0, self.size, self.size], self.size//10)

class TileGroup(pygame.sprite.Group):
    def draw(self, surface):
        tiles = self.sprites()
        surface_blit = surface.blit

        for tile in tiles:
            surface_blit(tile.background, tile.background_rect)
            self.spritedict[tile] = surface_blit(tile.image, tile.rect)
        self.lostsprites = []

       
class StateView():
    def __init__(self, directory, size=(800,800), pos=(0,0), board=None):
        """
        param directory:
            path to the directory containing the piece sprites
        param size:
            the size of the board
        param board:
            the state of the game
        """
        self.size = size
        self.pos = pos
        self.directory = directory

        if board is None:
            self.board = Board()
        else: 
            self.board = board

        self.sprites = pygame.sprite.Group()
        self.tiles = TileGroup()
        self.pieces = PieceGroup()

        self.convert_model_to_view()
        self.init_tile_effect_views()

    def init_tile_effect_views(self):
        tile_size = int(self.size[0] / 8)
        for i in range(8):
            for j in range(8):
                tile_effect_view = \
                    TileEffectView(Pos(i, j), (j*tile_size+self.pos[0], (7-i)*tile_size+self.pos[1]), tile_size)
                tile_effect_view.add(self.tiles, self.sprites)

    def convert_model_to_view(self):
        tile_size = int(self.size[0] / 8)
        for i in range(8):
            for j in range(8):
                pos = Pos(i, j)
                p = self.board.get(pos)
                if p is not None:
                    piece = PieceView(
                        self.directory,
                        p, 
                        p.player,
                        (i, j),
                        (j*tile_size+self.pos[0], (7-i)*tile_size+self.pos[1]), 
                        tile_size)
                    piece.add(self.pieces, self.sprites)
    
    def update(self, state):
        """
        """
        self.board = state
        for piece in self.pieces:
            piece.kill()
        self.convert_model_to_view()
    
    def draw(self, screen):
        """
        """
        board = pygame.Surface(self.size)
        board.fill(Colors.WHITE.value)

        tile_size = int(self.size[0] / 8)

        for i in range(8):
            for j in range(8):
                tile_color = Colors.CREAM.value if i % 2 == j % 2 else Colors.BLUE.value
                pygame.draw.rect(board, tile_color, (tile_size*j, tile_size*i, tile_size, tile_size))

        pygame.draw.rect(board, Colors.BLACK.value, [0, 0, 8*tile_size, 8*tile_size], 1)
        screen.blit(board, self.pos)

        self.tiles.draw(screen)
        self.pieces.draw(screen)




