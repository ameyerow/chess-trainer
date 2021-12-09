import pygame

from .utils.screen_pos import ScreenPos
from .utils.colors import Colors
from .piece_view import PieceView
from .piece_group import PieceGroup
from .tile_effect_view import TileEffectView
from .tile_group import TileGroup
from ..model.board import Board
from ..model.pos import Pos


class BoardView():
    def __init__(self, 
                image_directory: str, 
                size: int = 800, 
                board_offset: ScreenPos = ScreenPos(0, 0), 
                board_model: Board = None):

        self.size = size
        self.board_offset = board_offset
        self.image_directory = image_directory

        if board_model is None:
            self.board_model = Board()
        else: 
            self.board_model = board_model

        self.sprites = pygame.sprite.Group()
        self.tiles = TileGroup()
        self.pieces = PieceGroup()

        self.convert_model_to_view()
        self.init_tile_effect_views()

    def init_tile_effect_views(self):
        tile_size = int(self.size / 8)
        for rank in range(8):
            for file in range(8):
                board_pos = Pos(rank, file)
                screen_pos = ScreenPos(file * tile_size + self.board_offset.x, \
                                      (7-rank) * tile_size + self.board_offset.y)
                tile_effect_view = TileEffectView(board_pos, screen_pos, tile_size)
                tile_effect_view.add(self.tiles, self.sprites)

    def convert_model_to_view(self):
        tile_size = int(self.size / 8)
        for rank in range(8):
            for file in range(8):
                pos = Pos(rank, file)
                piece_model = self.board_model.get(pos)
                if piece_model is not None:
                    resting_screen_pos = ScreenPos(file * tile_size + self.board_offset.x, \
                                                  (7-rank) * tile_size + self.board_offset.y)
                    piece = PieceView(self.image_directory, piece_model, resting_screen_pos, tile_size)
                    piece.add(self.pieces, self.sprites)
    
    def update(self, board: Board):
        self.board_model = board
        for piece in self.pieces:
            piece.kill()
        self.convert_model_to_view()
    
    def draw(self, screen):
        board = pygame.Surface((self.size, self.size))
        board.fill(Colors.WHITE.value)

        tile_size = int(self.size / 8)

        for i in range(8):
            for j in range(8):
                tile_color = Colors.CREAM.value if i % 2 == j % 2 else Colors.BLUE.value
                pygame.draw.rect(board, tile_color, (tile_size*j, tile_size*i, tile_size, tile_size))

        pygame.draw.rect(board, Colors.BLACK.value, [0, 0, 8*tile_size, 8*tile_size], 1)
        screen.blit(board, (self.board_offset.x, self.board_offset.y))

        self.tiles.draw(screen)
        self.pieces.draw(screen)
