import pygame

from typing import List

from .controller import Controller
from .control_type import ControlType
from ..view.board_view import BoardView

class ComputerController(Controller):
    def handle_events(board_view: BoardView) -> ControlType:
        pass