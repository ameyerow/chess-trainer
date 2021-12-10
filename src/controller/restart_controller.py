import pygame

from typing import List, Set, Dict

from .controller import Controller
from .control_type import ControlType
from ..view.board_view import BoardView
from ..view.promotion_view import PromotionView
from ..view.utils.screen_pos import ScreenPos
from ..model.player import Player
from ..model.board import Board
from ..preprocess import StateNode


# TODO: IDEA: Restart screen should allow for changing whether computer is enabled!

class RestartController(Controller):

    def handle_events(self, board_view: BoardView) -> ControlType:
        new_control_type: ControlType = None
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN: 
                control_type = self.handle_mouse_down_event(mouse_pos, board_view)
                if control_type is not ControlType.Promotion:
                    new_control_type = control_type

        board_view.updateChildren(mouse_pos, pygame.mouse.get_pressed()[0])

        if new_control_type is None:
            return ControlType.Restart
        else:
            return new_control_type
    
    def handle_mouse_down_event(self, mouse_pos, board_view: BoardView) -> ControlType:
        mouse_screen_pos = ScreenPos(mouse_pos[0], mouse_pos[1])
        clicked_restart = board_view.restart_view.click(mouse_screen_pos)
        if clicked_restart:
            board_view.update(Board(), None, None)
            return ControlType.Player
        else:
            return ControlType.Restart