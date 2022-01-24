from typing import List, Set, Tuple
import pygame

from src.view.promotion_view import PromotionView

from .utils.screen_pos import ScreenPos
from .utils.colors import Colors
from .piece_view import PieceView
from .piece_group import PieceGroup
from .tile_effect_view import TileEffectView
from .restart_view import RestartView
from .tile_group import TileGroup
from .promotion_view import PromotionView
from .promotion_group import PromotionGroup
from ..model.player import Player
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

        self.detail = "Welcome to Repertoire Trainer!"
        self.moving_piece_view: PieceView = None
        self.last_move: Tuple[Pos, Pos] = (None, None)
        self.legal_moves_to_display: List[Pos] = []
        self.legal_captures_to_display: List[Pos] = []
        self.positive_hints_to_display: Set[Pos] = set()
        self.negative_hints_to_display: Set[Pos] = set()
        self.possible_promotion_dest: Pos = None
        self.possible_promotion_origin: Pos = None
        self.possible_promotion_player: Player = None
        self.prompt_for_restart = False

        self.sprites = pygame.sprite.Group()
        self.tiles = TileGroup()
        self.pieces = PieceGroup()
        self.promotion_views = PromotionGroup()
        self.restart_view = RestartView(self.size//8, self.board_offset)

        self.convert_model_to_view()
        self.init_tile_effect_views()
        self.init_promotion_views()

    def init_tile_effect_views(self):
        tile_size = self.size//8
        for rank in range(8):
            for file in range(8):
                board_pos = Pos(rank, file)
                screen_pos = ScreenPos(file * tile_size + self.board_offset.x, \
                                      (7-rank) * tile_size + self.board_offset.y)
                tile_effect_view = TileEffectView(board_pos, screen_pos, tile_size)
                tile_effect_view.add(self.tiles, self.sprites)

    def init_promotion_views(self):
        promotion_view_white = PromotionView(self.image_directory, int(self.size/8), self.board_offset, Player.WHITE)
        promotion_view_white.add(self.promotion_views, self.sprites)

        promotion_view_black = PromotionView(self.image_directory, int(self.size/8), self.board_offset, Player.BLACK)
        promotion_view_black.add(self.promotion_views, self.sprites)

    def convert_model_to_view(self):
        tile_size = self.size//8
        for rank in range(8):
            for file in range(8):
                pos = Pos(rank, file)
                piece_model = self.board_model.get(pos)
                if piece_model is not None:
                    resting_screen_pos = ScreenPos(file * tile_size + self.board_offset.x, \
                                                  (7-rank) * tile_size + self.board_offset.y)
                    piece = PieceView(self.image_directory, piece_model, resting_screen_pos, tile_size)
                    piece.add(self.pieces, self.sprites)
    
    def update(self, board: Board, origin: Pos, dest: Pos, comment: str = "", move_str: str = "", append_detail=False):
        """
        Updates the board view with a new model

        param board:
            The new board model.
        param origin:
            The origin position of the move that was just made.
        param dest:
            The destination position of the move that was just made.
        """
        self.board_model = board
        for piece in self.pieces:
            piece.kill()
        self.convert_model_to_view()

        if append_detail:
            self.detail = self.detail + "\n---------------\n" + (move_str + "\n" + comment.replace("{", "").replace("}", "").strip()).strip()
        else:
            self.detail = (move_str + "\n" + comment.replace("{", "").replace("}", "").strip()).strip()
        self.last_move = (origin, dest)
        self.legal_captures_to_display = []
        self.legal_moves_to_display = []
        self.positive_hints_to_display = set()
        self.negative_hints_to_display = set()
        self.possible_promotion_player = None
        self.possible_promotion_dest = None
        self.possible_promotion_origin = None
        self.prompt_for_restart = False

    def updateChildren(self, mouse_pos: Tuple[float, float], mouse_button_held_down: bool):
        if self.moving_piece_view is not None and mouse_button_held_down:
            mouse_screen_pos = ScreenPos(mouse_pos[0], mouse_pos[1])
        else:
            mouse_screen_pos = ScreenPos(-1, -1) 

        self.tiles.update(
            mouse_screen_pos, 
            self.legal_moves_to_display, 
            self.legal_captures_to_display, 
            self.positive_hints_to_display, 
            self.negative_hints_to_display, 
            self.last_move)
        self.pieces.update(
            mouse_screen_pos, 
            self.positive_hints_to_display, 
            self.negative_hints_to_display)
        self.promotion_views.update(
            self.possible_promotion_dest, 
            self.possible_promotion_player)
        self.restart_view.update(
            self.prompt_for_restart)
    
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

        font_size = tile_size // 4
        font = pygame.font.SysFont('Arial', font_size)
        padding = tile_size // 20
        # Draw file and rank letters and number onto screen
        files = ["a", "b", "c", "d", "e", "f", "g", "h"]
        for i in range(8):
            file_str = files[i]
            width, height = font.size(file_str)

            file = i
            rank = 0
            screen_pos = ScreenPos((file+1) * tile_size + self.board_offset.x - width - padding, \
                                   (7-rank+1) * tile_size + self.board_offset.y - height - padding)

            opposite_of_tile_color = Colors.CREAM.value if i % 2 != j % 2 else Colors.BLUE.value
            text_surface = font.render(file_str, True, opposite_of_tile_color)
            screen.blit(text_surface, (screen_pos.x, screen_pos.y))

        for i in range(8):
            rank_str = str(i+1)
            rank = i
            file = 0

            screen_pos = ScreenPos((file) * tile_size + self.board_offset.x + padding, \
                        (7-rank) * tile_size + self.board_offset.y + padding)

            opposite_of_tile_color = Colors.CREAM.value if i % 2 != j % 2 else Colors.BLUE.value
            text_surface = font.render(rank_str, True, opposite_of_tile_color)
            screen.blit(text_surface, (screen_pos.x, screen_pos.y))

        self.pieces.draw(screen)
        self.promotion_views.draw(screen)
        self.restart_view.draw(screen)
