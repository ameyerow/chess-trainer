import itertools

from .piece import Piece
from ..pos import Pos
from ..board import *


class Queen(Piece):
    def __init__(self, pos: Pos, player: Player):
        super().__init__(pos, player, "Q")

    def can_pin_orthogonally(self) -> bool:
        return True

    def can_pin_diagonally(self) -> bool:
        return True
    
    def attacks_square_from_position(self, pos: Pos, dest: Pos, board) -> bool:
        if pos == dest:
            return False
        return self.__bishop_attacks_square_from_position(pos, dest, board) or \
               self.__rook_attacks_square_from_position(pos, dest, board)

    def __bishop_attacks_square_from_position(self, pos: Pos, dest: Pos, board) -> bool:
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

    def __rook_attacks_square_from_position(self, pos: Pos, dest: Pos, board) -> bool:
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
        # A Queen acts as a bishop and a rook so we run the checks for those
        # two pieces
        if origin_hint is not None:
            return Piece.get_hint_origin(origin_hint, Queen, board)

        rank = destination_pos.rank
        file = destination_pos.file

        max_straight = max([rank, file, 7 - rank, 7 - file])
        for offset in range(1, max_straight + 1):
            for o in [offset, -offset]:
                if 0 <= rank + o < 8:
                    pos = Pos(rank + o, file)
                    queen = board.get(pos)
                    if isinstance(queen, Queen) and queen.player == board.current_player:
                        return pos
                if 0 <= file + o < 8:
                    pos = Pos(rank, file + o)
                    queen = board.get(pos)
                    if isinstance(queen, Queen) and queen.player == board.current_player:
                        return pos

        max_diag = max([rank, file, 7-rank, 7-file])
        for offset in range(1, max_diag+1):
            for i, j in itertools.product([offset, -offset], repeat=2):
                if 0 <= rank + i < 8 and 0 <= file + j < 8:
                    pos = Pos(rank + i, file + j)
                    queen = board.get(pos)
                    if isinstance(queen, Queen) and queen.player == board.current_player:
                        return pos

        raise PieceNotFoundException("Didn't find Queen's origin")

    def is_dest_reachable(self, dest: Pos, board) -> bool:
        is_dest_reachable_bishop = self.__is_dest_reachable_bishop(dest, board)
        is_dest_reachable_rook = self.__is_dest_reachable_rook(dest, board)

        return is_dest_reachable_bishop or is_dest_reachable_rook
    
    def __is_dest_reachable_bishop(self, dest: Pos, board) -> bool:
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

    def __is_dest_reachable_rook(self, dest: Pos, board) -> bool:
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
        return Queen(self.pos, self.player)
