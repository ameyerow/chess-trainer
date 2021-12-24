import sys
import pygame
import random

from typing import List, Set, Dict

from .controller import Controller
from .control_type import ControlType
from ..view.board_view import BoardView
from ..model.board import Board
from ..preprocess import StateNode

class ComputerController(Controller):
    def __init__(self, state_map: Dict[str, Set[StateNode]]):
        self.state_map = state_map

    def handle_events(self, board_view: BoardView) -> ControlType:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
                
        possible_continuations = list(self.state_map[str(board_view.board_model)])
        if not possible_continuations:
            return ControlType.Computer

        weights = list(map(lambda x: x.depth, possible_continuations))
        node: StateNode = random.choices(possible_continuations, weights=weights, k=1)[0]

        origin = board_view.board_model.get_move_origin(node.move)
        dest = board_view.board_model.get_move_destination(node.move)
        new_board_model = Board(board_str=node.state)
        board_view.update(new_board_model, origin, dest, comment=node.comment, move_str=node.move, append_detail=True)

        possible_continuations = self.state_map[str(new_board_model)]
        if not possible_continuations:
            board_view.prompt_for_restart = True
            return ControlType.Restart
        else:
            return ControlType.Player