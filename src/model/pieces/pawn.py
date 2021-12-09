from .piece import Piece
from ..pos import Pos
from ..player import Player
from ..board import *


class Pawn(Piece):
    def __init__(self, pos: Pos, player: Player, is_capturable_en_passant=False):
        super().__init__(pos, player, "P")
        self.is_capturable_en_passant = is_capturable_en_passant

    def __str__(self) -> str:
        if self.is_capturable_en_passant:
            return "G" if self.player is Player.WHITE else "g"
        else:
            return self.name if self.player is Player.WHITE else self.name.lower()

    def can_pin_orthogonally(self) -> bool:
        return False
    
    def can_pin_diagonally(self) -> bool:
        return False
    
    def attacks_square_from_position(self, pos: Pos, dest: Pos, board) -> bool:
        forward_delta = 1 if self.player is Player.WHITE else -1
        can_attack_rank = pos.rank + forward_delta

        first_attack_location = Pos(can_attack_rank, pos.file-1)
        second_attack_location = Pos(can_attack_rank, pos.file+1)

        return dest == first_attack_location or dest == second_attack_location

    @staticmethod
    def get_origin(destination_pos: Pos, board, origin_hint: str = None) -> Pos:
        player_modifier = 1 if board.current_player is Player.WHITE else -1
        if origin_hint is not None:
            # Hint will always be a letter indicating the file
            file = Pos.index_from_file(origin_hint)
            rank = destination_pos.rank - player_modifier
            pos = Pos(rank, file)
            if isinstance(board.get(pos), Pawn) and board.get(pos).player == board.current_player:
                return pos
        else:
            rank = destination_pos.rank
            file = destination_pos.file
            one_space = Pos(rank - player_modifier, file)
            two_space = Pos(rank - 2*player_modifier, file)
            if isinstance(board.get(one_space), Pawn) and board.get(one_space).player == board.current_player:
                return one_space
            elif isinstance(board.get(two_space), Pawn) and board.get(two_space).player == board.current_player:
                return two_space
        raise PieceNotFoundException("Didn't find Pawn's origin")

    def is_dest_reachable(self, dest: Pos, board) -> bool:
        rank_diff = dest.rank - self.pos.rank
        file_diff = dest.file - self.pos.file
        
        # The 'forward' direction is dependent on which player's pawn it is
        forward_delta = 1 if self.player is Player.WHITE else -1

        if rank_diff == forward_delta and file_diff == 0 and board.is_empty(dest):
            # A normal pawn move, forward one square
            return True
        elif rank_diff == 2 * forward_delta and file_diff == 0 and board.is_empty(dest) and \
                board.is_empty(Pos(rank=self.pos.rank + forward_delta, file=self.pos.file)) and \
                    self.pos.rank == (1 if forward_delta == 1 else 6):
            # If a pawn is on its starting rank it can move forward two squares 
            return True
        elif rank_diff == forward_delta and abs(file_diff) == 1:
            # A pawn capture is possible if the destination is capturable or the pawn at its
            # shoulder is capturable en passant
            en_passant_pos = Pos(rank=self.pos.rank, file=dest.file)
            piece = board.get(en_passant_pos)
            shoulder_pawn_is_en_passant = piece is not None and \
                isinstance(piece, Pawn) and \
                piece.player != self.player and \
                piece.is_capturable_en_passant
            
            dest_is_capturable = not board.is_empty(dest) and board.get(dest).player is not self.player 
            return dest_is_capturable or shoulder_pawn_is_en_passant
        return False
    
    def __copy__(self):
        return Pawn(self.pos, self.player, self.is_capturable_en_passant)