import pygame

from typing import List, Set, Dict

from .controller import Controller
from .control_type import ControlType
from ..view.board_view import BoardView
from ..view.promotion_view import PromotionView
from ..view.utils.screen_pos import ScreenPos
from ..model.player import Player
from ..preprocess import StateNode


class PromotionController(Controller):
    def __init__(self, 
                state_map: Dict[str, Set[StateNode]], 
                computer_response_enabled: bool = False, 
                training_enabled: bool = True):
        self.state_map = state_map
        self.computer_response_enabled = computer_response_enabled
        self.training_enabled = training_enabled

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
            return ControlType.Promotion
        else:
            return new_control_type
    
    def handle_mouse_down_event(self, mouse_pos, board_view: BoardView) -> ControlType:
        promotion_view = self.get_promotion_view(board_view)
        mouse_screen_pos = ScreenPos(mouse_pos[0], mouse_pos[1])
        promotion_piece = promotion_view.click(mouse_screen_pos)
        if promotion_piece is None:
            board_view.possible_promotion_dest = None
            board_view.possible_promotion_origin = None
            board_view.possible_promotion_player = None
            return ControlType.Player
        else:
            board_model = board_view.board_model
            origin = board_view.possible_promotion_origin
            dest = board_view.possible_promotion_dest
            # Since the move is legal we can convert this origin->dest to a proper move in pgn format
            # and update the board with it.
            move_pgn = board_model.move_to_pgn_notation(origin, dest, promotion_piece=promotion_piece)
            new_board_model = board_model.update(move_pgn)
            
            # If, however, this isn't a proper continuation in our state map we adjust the displayed hints
            # and have the player make another move.
            possible_continuations = self.state_map[str(board_model)]
            if self.training_enabled and StateNode(move_pgn, str(new_board_model)) not in possible_continuations:
                move_origin = board_model.get_move_origin(move_pgn)
                # At this point we know the move the player made was not a correct continuation but it may
                # have been with a piece that has a correct move in the state map. If so we want to give the
                # player a hint that the piece that was attempted to be moved was correct but the destination
                # square was incorrect. Otherwise we want to tell the player that they should not try moving
                # that piece again.
                correct_piece = False
                for node in possible_continuations:
                    possible_move_origin = board_model.get_move_origin(node.move)
                    if move_origin == possible_move_origin:
                        correct_piece = True
                        break
                if correct_piece:
                    board_view.positive_hints_to_display.add(origin)
                else:
                    board_view.negative_hints_to_display.add(origin)
                return ControlType.Player
            else:
                # In the case that the move was a proper continuation we update the board view with the new
                # model
                board_view.update(new_board_model, origin, dest)

                if self.computer_response_enabled:
                    return ControlType.Computer
                else:
                    return ControlType.Player
    
    def get_promotion_view(self, board_view) -> PromotionView:
        player = board_view.board_model.current_player
        for promotion_view in board_view.promotion_views.sprites():
            if promotion_view.player == player:
                return promotion_view
        return None