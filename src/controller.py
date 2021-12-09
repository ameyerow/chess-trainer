from enum import Enum
import pygame

from src.model.player import Player

pygame.init()

import os
import random
import sys

from typing import Tuple, List, Set, Dict

from .view.board_view import BoardView
from .view.piece_view import PieceView
from .view.tile_effect_view import TileEffectView
from .view.utils.screen_pos import ScreenPos
from .view.utils.colors import Colors
from .model.pos import Pos
from .model.board import Board
from .preprocess import StateNode


class InputState(Enum):
    PLAYER=0
    PROMOTION=1
    AI = 2


SCREEN_SIZE = (800, 800)

def display_board(state_map: Dict[str, Set[StateNode]]):
    image_directory = os.path.join(os.getcwd(), "sprites")

    game_display = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Repertoire Trainer")

    icon = pygame.image.load(os.path.join(image_directory, "BLACK_Q.png"))
    pygame.display.set_icon(icon)

    board_view = BoardView(image_directory, size=760, board_offset=ScreenPos(20, 20))
    past_states: List[Board] = [board_view.board_model]

    moving_piece_view: PieceView = None
    last_move: Tuple[Pos, Pos] = (None, None)
    legal_moves: List[Pos] = []
    legal_captures: List[Pos] = []
    positive_hints: Set[Pos] = set()
    negative_hints: Set[Pos] = set()
    possible_promotion_pos: Pos = None
    possible_promotion_player: Player = None

    ai_turn = False
    training_mode = False

    while True:
        if ai_turn:
            curr_state = past_states[-1]
            possible_continuations = list(state_map[str(curr_state)])
            if not possible_continuations:
                break
            weights = list(map(lambda x: x.depth, possible_continuations))
            node: StateNode = random.choices(possible_continuations, weights=weights, k=1)[0]
            print(node.move, weights[possible_continuations.index(node)] / sum(weights))

            new_board_model = Board(board_str=node.state)
            board_view.update(new_board_model)
            past_states.append(board_view.board_model)

            last_move = (None, None)
            legal_moves = []
            legal_captures = []

            ai_turn = False
        else:
            possible_continuations = state_map[str(past_states[-1])]
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for piece_view in board_view.pieces:
                        piece_view: PieceView = piece_view
                        if piece_view.rect.collidepoint(mouse_pos):
                            for other_piece in board_view.pieces:
                                if other_piece != piece_view:
                                    other_piece.selected = False

                            piece_view.selected = True
                            legal_moves, legal_captures = piece_view.piece_model.legal_moves(board_view.board_model)

                            if pygame.mouse.get_pressed()[0]:
                                piece_view.resting = False
                                moving_piece_view = piece_view

                if event.type == pygame.MOUSEBUTTONUP:
                    if moving_piece_view is not None:
                        for tile in board_view.tiles:
                            tile: TileEffectView = tile
                            if tile.rect.collidepoint(mouse_pos):
                                origin = moving_piece_view.piece_model.pos
                                dest = tile.board_pos

                                move_type = board_view.board_model.is_legal_move(dest, moving_piece_view.piece_model)
                                if move_type.is_legal():
                                    if board_view.board_model.move_requires_promotion(origin, dest):
                                        possible_promotion_player = moving_piece_view.piece_model.player
                                        possible_promotion_pos = dest
                                        break

                                    hint_str = "Possible continuations: "
                                    for node in possible_continuations:
                                        hint_str = hint_str + node.move + " "
                                    print(hint_str)

                                    move_pgn = board_view.board_model.move_to_pgn_notation(origin, dest)
                                    new_board_model = board_view.board_model.update(move_pgn)
                                    
                                    if training_mode and StateNode(move_pgn, str(new_board_model)) not in possible_continuations:
                                        move_origin = board_view.board_model.get_move_origin(move_pgn)
                                        correct_piece = False
                                        for node in possible_continuations:
                                            possible_move_origin = board_view.board_model.get_move_origin(node.move)
                                            if move_origin == possible_move_origin:
                                                correct_piece = True
                                                break
                                        if correct_piece:
                                            positive_hints.add(origin)
                                        else:
                                            negative_hints.add(origin)

                                        break

                                    board_view.update(new_board_model)
                                    past_states.append(board_view.board_model)

                                    last_move = (origin, dest)
                                    legal_moves = []
                                    legal_captures = []
                                    positive_hints = set()
                                    negative_hints = set()
                                    # ai_turn = True
                                break
                    for piece_view in board_view.pieces:
                        piece_view.resting = True
                        moving_piece_view = None

            if moving_piece_view is not None and pygame.mouse.get_pressed()[0]:
                board_view.tiles.update(mouse_pos, legal_moves, legal_captures, positive_hints, negative_hints, last_move)
            else:
                board_view.tiles.update((-1,-1), legal_moves, legal_captures, positive_hints, negative_hints, last_move)   

            board_view.pieces.update(ScreenPos(mouse_pos[0], mouse_pos[1]), positive_hints, negative_hints)
            board_view.promotion_views.update(possible_promotion_pos, possible_promotion_player)

        game_display.fill(Colors.WHITE.value)
        board_view.draw(game_display)
        pygame.display.update()