from .piece import Piece
from .rook import Rook
from ..pos import Pos
from ..player import Player
from ..board import *


class King(Piece):
    def __init__(self, pos: Pos, player: Player, has_moved = False, in_check=False):
        super().__init__(pos, player, "K")
        self.has_moved = has_moved
        self.in_check = in_check

    def can_pin_orthogonally(self) -> bool:
        return False
    
    def can_pin_diagonally(self) -> bool:
        return False

    def attacks_square_from_position(self, pos: Pos, dest: Pos, board) -> bool:
        rank_diff = dest.rank - pos.rank
        file_diff = dest.file - pos.file

        return abs(rank_diff) <= 1 and abs(file_diff) <= 1

    @staticmethod
    def get_origin(destination_pos: Pos, board, origin_hint: str = None) -> Pos:
        return board.get_king_pos(board.current_player)
    
    def is_dest_reachable(self, dest: Pos, board) -> bool:
        # Castling: king can't pass through check or be in check, the rook and king can't have moved,
        # and path between rook and king must be empty
        if dest == Pos.index("g1", player=self.player) and not self.has_moved:
            # Short castle
            path_is_empty = board.is_empty("f1", player=self.player) and \
                            board.is_empty("g1", player=self.player)

            rook = board.get("h1", player=self.player)
            rook_hasnt_moved = isinstance(rook, Rook) and not rook.has_moved

            not_passing_through_check = not self.in_check and \
                                        not board.is_under_attack("f1", player=self.player) and \
                                        not board.is_under_attack("g1", player=self.player)

            return path_is_empty and rook_hasnt_moved and not_passing_through_check
        elif dest == Pos.index("c1", player=self.player) and not self.has_moved:
            # Long castle
            path_is_empty = board.is_empty("d1", player=self.player) and \
                            board.is_empty("c1", player=self.player) and \
                            board.is_empty("b1", player=self.player)

            rook = board.get("a1", player=self.player)
            rook_hasnt_moved = isinstance(rook, Rook) and not rook.has_moved

            not_passing_through_check = not self.in_check and \
                                        not board.is_under_attack("d1", player=self.player) and \
                                        not board.is_under_attack("c1", player=self.player)

            return path_is_empty and rook_hasnt_moved and not_passing_through_check
        else:
            rank_diff = dest.rank - self.pos.rank
            file_diff = dest.file - self.pos.file

            correct_move_shape = abs(rank_diff) <= 1 and abs(file_diff) <= 1
            moving_into_check = board.is_under_attack(dest, transparent_piece=self)

            return correct_move_shape and not moving_into_check

    def __copy__(self):
        return King(self.pos, self.player, has_moved=self.has_moved, in_check=self.in_check)