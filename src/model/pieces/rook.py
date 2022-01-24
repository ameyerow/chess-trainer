from .piece import Piece
from ..pos import Pos
from ..board import *


class Rook(Piece):
    def __init__(self, pos: Pos, player: Player, has_moved=False):
        super().__init__(pos, player, "R")
        self.has_moved = has_moved

    def can_pin_orthogonally(self) -> bool:
        return True
    
    def can_pin_diagonally(self) -> bool:
        return False

    def attacks_square_from_position(self, pos: Pos, dest: Pos, board) -> bool:
        if pos == dest:
            return False

        rank_diff = dest.rank - pos.rank
        file_diff = dest.file - pos.file

        # The rook can only move along either a rank or file
        if not (rank_diff == 0 or file_diff == 0):
            return False

        if rank_diff == 0:
            min_file = min(dest.file, pos.file)
            max_file = max(dest.file, pos.file)
            rank = pos.rank # Same as dest.rank

            for file in range(min_file+1, max_file):
                curr_pos = Pos(rank, file)
                if curr_pos == self.pos or board.get(curr_pos) is None:
                    continue
                else:
                    return False
        else:
            min_rank = min(dest.rank, pos.rank)
            max_rank = max(dest.rank, pos.rank)
            file = pos.file # Same as dest.file

            for rank in range(min_rank+1, max_rank):
                curr_pos = Pos(rank, file)
                if curr_pos == self.pos or board.get(curr_pos) is None:
                    continue
                else:
                    return False
        return True

    @staticmethod
    def get_origin(destination_pos: Pos, board, origin_hint: str = None) -> Pos:
        # The rook's origin had to be on one of the straight lines from the
        # destination
        if origin_hint is not None:
            return Piece.get_hint_origin(origin_hint, Rook, board)

        rank = destination_pos.rank
        file = destination_pos.file

        possible_origin_pieces: List[Rook] = []
        max_straight = max([rank, file, 7 - rank, 7 - file])
        for offset in range(1, max_straight + 1):
            for o in [offset, -offset]:
                if 0 <= rank + o < 8:
                    pos = Pos(rank + o, file)
                    rook = board.get(pos)
                    if isinstance(rook, Rook) and rook.player == board.current_player:
                        possible_origin_pieces.append(rook)
                if 0 <= file + o < 8:
                    pos = Pos(rank, file + o)
                    rook = board.get(pos)
                    if isinstance(rook, Rook) and rook.player == board.current_player:
                        possible_origin_pieces.append(rook)
        
        for piece in possible_origin_pieces:
            if piece.is_dest_reachable(destination_pos, board):
                return piece.pos

        raise PieceNotFoundException("Didn't find Rook's origin")
    
    def is_dest_reachable(self, dest: Pos, board) -> bool:
        rank_diff = dest.rank - self.pos.rank
        file_diff = dest.file - self.pos.file

        # The rook can only move along either a rank or file
        if not (rank_diff == 0 or file_diff == 0):
            return False

        # The path between pos and dest has to be empty, excluding dest itself
        if rank_diff == 0:
            delta = 1 if file_diff > 0 else -1
            for i in range(self.pos.file + delta, dest.file, delta):
                if board.get(Pos(rank=dest.rank, file=i)) is not None:
                    return False
        elif file_diff == 0:
            delta = 1 if rank_diff > 0 else -1
            for i in range(self.pos.rank + delta, dest.rank, delta):
                if board.get(Pos(rank=i, file=dest.file)) is not None:
                    return False
        
        # The destination is reachable if execution has reached this point
        return True

    def __copy__(self):
        return Rook(self.pos, self.player, self.has_moved)
