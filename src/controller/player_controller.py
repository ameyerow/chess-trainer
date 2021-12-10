import pygame
import sys

from typing import Dict, List, Set, Tuple

from .controller import Controller
from .control_type import ControlType
from ..view.board_view import BoardView
from ..preprocess import StateNode


class PlayerController(Controller):
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
                self.handle_mouse_down_event(mouse_pos, board_view)

            if event.type == pygame.MOUSEBUTTONUP: 
                control_type = self.handle_mouse_up_event(mouse_pos, board_view)
                if control_type is not ControlType.Player:
                    new_control_type = control_type
                # Once we release the mouse button, no piece should be moving anymore.
                for piece_view in board_view.pieces:
                    piece_view.resting = True
                    board_view.moving_piece_view = None

        board_view.updateChildren(mouse_pos, pygame.mouse.get_pressed()[0])

        if new_control_type is None:
            return ControlType.Player
        else:
            return new_control_type

    def handle_mouse_down_event(self, mouse_pos: Tuple[float, float], board_view: BoardView):
        # Determine which piece -- if any -- was pressed down on.
        for piece_view in board_view.pieces:
            if piece_view.rect.collidepoint(mouse_pos):
                # Since only one piece can be selected at a time, deselect all other pieces that we 
                # did not just press down upon.
                for other_piece in board_view.pieces:
                    if other_piece != piece_view:
                        other_piece.selected = False

                # Select the piece we pressed down on and display its legal moves and captures on the board.
                piece_view.selected = True
                legal_moves, legal_captures = piece_view.piece_model.legal_moves(board_view.board_model)
                board_view.legal_moves_to_display = legal_moves
                board_view.legal_captures_to_display = legal_captures
                
                # If we are holding the mouse button down, start moving the piece.
                if pygame.mouse.get_pressed()[0]:
                    piece_view.resting = False
                    board_view.moving_piece_view = piece_view

    def handle_mouse_up_event(self, mouse_pos: Tuple[float, float], board_view: BoardView) -> ControlType:
        moving_piece_view = board_view.moving_piece_view
        board_model = board_view.board_model
        if moving_piece_view is None:
            return ControlType.Player
        else:
            # A piece is currently being moved at the time we released the mouse button. This means
            # it is possible that a move was made, we must check if we are allowed to make this move.
            # If so we update the board model and board view and change the control type accordingly.
            for tile in board_view.tiles:
                # Find the tile which we released our piece over -- this is the position we are
                # attempting to move the piece to.
                if tile.rect.collidepoint(mouse_pos):
                    # The moving piece's position is the origin of our potential move.
                    origin = moving_piece_view.piece_model.pos
                    # The potential destination is the tile's position.
                    dest = tile.board_pos

                    # Check if the move is legal.
                    move_type = board_model.is_legal_move(dest, moving_piece_view.piece_model)
                    if move_type.is_legal():
                        # If we are attempting to promote a pawn, we need to promt the user to select which
                        # piece they want to promote to. We need to change the control type of the game to
                        # accomodate this.
                        if board_model.move_requires_promotion(origin, dest):
                            board_view.possible_promotion_player = board_view.moving_piece_view.piece_model.player
                            board_view.possible_promotion_dest = dest
                            board_view.possible_promotion_origin = origin
                            return ControlType.Promotion

                        # Since the move is legal we can convert this origin->dest to a proper move in pgn format
                        # and update the board with it.
                        move_pgn = board_model.move_to_pgn_notation(origin, dest)
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

                            # If there are no continuations from this line, prompt to restart the game
                            possible_continuations = self.state_map[str(new_board_model)]
                            if self.training_enabled and not possible_continuations:
                                board_view.prompt_for_restart = True
                                return ControlType.Restart

                            if self.computer_response_enabled:
                                return ControlType.Computer
                            else:
                                return ControlType.Player