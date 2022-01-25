import pygame
pygame.init()
import os

from typing import Dict, Set

from .preprocess import state_map_from_pgn, StateNode
from .controller.controller import Controller
from .controller.control_type import ControlType
from .controller.player_controller import PlayerController
from .controller.computer_controller import ComputerController
from .controller.promotion_controller import PromotionController
from .controller.restart_controller import RestartController
from .view.utils.colors import Colors
from .view.board_view import BoardView
from .view.utils.screen_pos import ScreenPos
from .view.utils.text import multiLineSurface

TILE_SIZE = 100
BORDER = 20
DETAIL_PANEL_WIDTH = 300
SCREEN_SIZE = (TILE_SIZE*8 + 3*BORDER + DETAIL_PANEL_WIDTH, TILE_SIZE*8 + 2*BORDER)
COMPUTER_RESPONSE_ENABLED = True
TRAINING_ENABLED = True

# TODO: Add accuracy tracker!!

def main():
    pgn_path = os.path.join(os.getcwd(), "pgns/FrenchDefense.pgn")
    state_map = state_map_from_pgn(pgn_path)

    display_board(state_map)

def display_board(state_map: Dict[str, Set[StateNode]]):
    image_directory = os.path.join(os.getcwd(), "sprites")

    game_display = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Repertoire Trainer")

    icon = pygame.image.load(os.path.join(image_directory, "BLACK_Q.png"))
    pygame.display.set_icon(icon)

    board_view = BoardView(image_directory, size=TILE_SIZE*8, board_offset=ScreenPos(BORDER, BORDER))

    controllers: Dict[ControlType, Controller] = {}
    controllers[ControlType.Player] = PlayerController(
        state_map, 
        computer_response_enabled=COMPUTER_RESPONSE_ENABLED,
        training_enabled=TRAINING_ENABLED)
    controllers[ControlType.Promotion] = PromotionController(
        state_map,
        computer_response_enabled=COMPUTER_RESPONSE_ENABLED,
        training_enabled=TRAINING_ENABLED)
    controllers[ControlType.Computer] = ComputerController(state_map)
    controllers[ControlType.Restart] = RestartController()

    active_control_type = ControlType.Player

    while True:
        controller: Controller = controllers[active_control_type]
        active_control_type = controller.handle_events(board_view)
 
        game_display.fill(Colors.WHITE.value)
        board_view.draw(game_display)

        # TODO: Move this somewhere permanent
        font_size = TILE_SIZE // 5
        font = pygame.font.SysFont('Arial', font_size)
        text_surface = multiLineSurface(board_view.detail, font, pygame.Rect(0, 0, DETAIL_PANEL_WIDTH, TILE_SIZE*8), Colors.BLACK.value, Colors.WHITE.value)
        game_display.blit(text_surface, (840, 20))

        pygame.display.update()

if __name__ == "__main__":
    main()






                 