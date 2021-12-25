import itertools

from .piece import Piece
from ..pos import Pos
from ..player import Player
from ..board import *
from ..exceptions import PieceNotFoundException


class Bishop(Piece):
    def __init__(self, pos: Pos, player: Player):
        super().__init__(pos, player, "B")

    def can_pin_orthogonally(self) -> bool:
        return False
    
    def can_pin_diagonally(self) -> bool:
        return True

    def attacks_square_from_position(self, pos: Pos, dest: Pos, board) -> bool:
        # A slope of 1 or -1 must exists between the piece position and the position being attacked.
        rank_diff = dest.rank - pos.rank
        file_diff = dest.file - pos.file

        if not (rank_diff != 0 and file_diff != 0 and abs(rank_diff / file_diff) == 1):
            return False

        # Iterate along the diagonal and check if each square in between the piece's position and the
        # destination is empty. If we encouter the current location of this piece we consider it empty!
        delta_rank = 1 if rank_diff < 0 else -1
        delta_file = 1 if file_diff < 0 else -1

        for rank, file in zip(range(dest.rank+delta_rank, pos.rank, delta_rank),\
                              range(dest.file+delta_file, pos.file, delta_file)):
            curr_pos = Pos(rank, file)
            if curr_pos == self.pos or board.get(curr_pos) is None:
                continue
            else:
                return False

        return True    
    
    @staticmethod
    def get_origin(destination_pos: Pos, board, origin_hint: str = None) -> Pos:
        # The bishop's origin had to be on one of the diagonals through the 
        # destination
        if origin_hint is not None:
            return Piece.get_hint_origin(origin_hint, Bishop, board)

        rank = destination_pos.rank
        file = destination_pos.file

        possible_origin_pieces: List[Bishop] = []
        max_diag = max([rank, file, 7 - rank, 7 - file])
        for offset in range(1, max_diag+1):
            for i, j in itertools.product([offset, -offset], repeat=2):
                if 0 <= rank + i < 8 and 0 <= file + j < 8:
                    pos = Pos(rank + i, file + j)
                    bishop = board.get(pos)
                    if isinstance(bishop, Bishop) and bishop.player == board.current_player:
                        possible_origin_pieces.append(bishop)

        for piece in possible_origin_pieces:
            if piece.is_dest_reachable(destination_pos, board):
                return piece.pos

        raise PieceNotFoundException("Didn't find Bishop's origin")

    def is_dest_reachable(self, dest: Pos, board) -> bool:
        rank_diff = dest.rank - self.pos.rank
        file_diff = dest.file - self.pos.file

        # The slope of the move has to be 1, a diagonal from the current location
        if not (rank_diff != 0 and file_diff != 0 and abs(rank_diff / file_diff) == 1):
            return False
            
        # The path between pos and dest has to be empty
        delta_rank = 1 if rank_diff > 0 else -1
        delta_file = 1 if file_diff > 0 else -1
        for i, j in zip(range(self.pos.rank + delta_rank, dest.rank, delta_rank), \
                        range(self.pos.file + delta_file, dest.file, delta_file)):
            if board.get(Pos(rank=i, file=j)) is not None:
                    return False

        # The destination is reachable if execution has reached this point
        return True

    def __copy__(self):
        return Bishop(self.pos, self.player)