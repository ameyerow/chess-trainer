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

SCREEN_SIZE = (800, 800)
COMPUTER_RESPONSE_ENABLED = True
TRAINING_ENABLED = True

def main():
    pgn_path = os.path.join(os.getcwd(), "pgns/d4Dynamite.pgn")
    state_map = state_map_from_pgn(pgn_path)

    print()

    display_board(state_map)

def display_board(state_map: Dict[str, Set[StateNode]]):
    image_directory = os.path.join(os.getcwd(), "sprites")

    game_display = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Repertoire Trainer")

    icon = pygame.image.load(os.path.join(image_directory, "BLACK_Q.png"))
    pygame.display.set_icon(icon)

    board_view = BoardView(image_directory, size=760, board_offset=ScreenPos(20, 20))

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
        pygame.display.update()

if __name__ == "__main__":
    main()






                 