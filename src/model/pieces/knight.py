import itertools

from .piece import Piece
from ..pos import Pos
from ..board import *


class Knight(Piece):

    def __init__(self, pos: Pos, player: Player):
        super().__init__(pos, player, "N")

    def can_pin_orthogonally(self) -> bool:
        return False
    
    def can_pin_diagonally(self) -> bool:
        return False

    def attacks_square_from_position(self, pos: Pos, dest: Pos, board) -> bool:
        rank_diff = pos.rank - dest.rank
        file_diff = pos.file - dest.file  

        shape = (abs(rank_diff), abs(file_diff))
        correct_move_shape = shape == (1, 2) or shape == (2, 1)
        return correct_move_shape

    @staticmethod
    def get_origin(destination_pos: Pos, board, origin_hint: str = None) -> Pos:
        if origin_hint is not None:
            return Piece.get_hint_origin(origin_hint, Knight, board)

        rank = destination_pos.rank
        file = destination_pos.file

        for i, j in itertools.product([1, -1], [2, -2]):
            if 0 <= rank + i < 8 and 0 <= file + j < 8:
                pos = Pos(rank + i, file + j)
                knight = board.get(pos)
                if isinstance(knight, Knight) and knight.player == board.current_player:
                    return pos
            if 0 <= rank + j < 8 and 0 <= file + i < 8:
                pos = Pos(rank + j, file + i)
                knight = board.get(pos)
                if isinstance(knight, Knight) and knight.player == board.current_player:
                    return pos
        raise PieceNotFoundException("Didn't find Knight's origin")
    
    def is_dest_reachable(self, dest: Pos, board) -> bool:
        rank_diff = self.pos.rank - dest.rank
        file_diff = self.pos.file - dest.file  

        shape = (abs(rank_diff), abs(file_diff))
        correct_move_shape = shape == (1, 2) or shape == (2, 1)
        return correct_move_shape

    def __copy__(self):
        return Knight(self.pos, self.player)