from __future__ import annotations
import abc

from typing import List, Tuple, Type

from ..pos import Pos
from ..player import Player
from ..move import Move
from ..exceptions import PieceNotFoundException

class Piece(metaclass=abc.ABCMeta):
    def __init__(self, pos: Pos, player: Player, name: str):
        self.pos = pos
        self.player = player
        self.name = name

    def __str__(self) -> str:
        return self.name if self.player is Player.WHITE else self.name.lower()

    @abc.abstractmethod
    def can_pin_orthogonally(self) -> bool:
        """
        return:
            True if the piece can pin orthogonally, False otherwise
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def can_pin_diagonally(self) -> bool:
        """
        return:
            True if the piece can pin diagonally, False otherwise
        """
        raise NotImplementedError

    @abc.abstractmethod
    def attacks_square_from_position(self, pos: Pos, dest: Pos, board) -> bool:
        """
        Determines if the current piece could attack a given location from a tile on the board --
        that it could move there legally. The current piece's position is considered to be empty.

        param pos:
            The position the piece should be imagined existing in
        param dest:
            The position that is attempting to be attacked
        param board:
            The current state of the board

        return:
            True if the current piece could attack dest from pos, False otherwise
        """
        raise NotImplementedError

    def legal_moves(self, board) -> Tuple[List[Pos], List[Pos]]:
        """
        Returns a list of legal positions the piece can move.

        return:
            List of positions
        """
        # TODO: speed this up
        moves = []
        captures = []
        for i in range(8):
            for j in range(8):
                dest = Pos(i, j)
                move: Move = board.is_legal_move(dest, self)
                if move.is_capture() and move.is_legal():
                    captures.append(dest)
                elif move.is_legal():
                    moves.append(dest)
        return moves, captures


    @abc.abstractmethod
    def is_dest_reachable(self, dest: Pos, board) -> bool:
        """
        Given the type of the current piece is the destination position reachable: is the move the
        correct shape and is the path clear? At this point you may assume that you are not attempting
        to move to your current position and that the destination square is not occupied by your own
        piece.

        param dest:
            The position the piece is attempting to move
        param board:
            The current state of the board

        return:
            True if the destination is reachable, False otherwise
        """
        raise NotImplementedError

    def maintains_pin(self, dest: Pos, board) -> bool:
        """
        Does the current move maintain every pin if they exists? At this point you may assume that the 
        destination tile constites a reachable tile for that piece -- that it is of the correct shape 
        and the path is clear.

        param dest:
            The position the piece is attempting to move
        param board:
            The current state of the board

        return:
            True if the a pin is maintained or one doesn't exist, False otherwise
        """
        
        king_pos = board.get_king_pos(board.current_player)
        # A king can't be pinned.
        if king_pos == self.pos:
            return True

        rank_diff = king_pos.rank - self.pos.rank 
        file_diff = king_pos.file - self.pos.file

        # If the piece is on the same rank as the King we must check if any pin along the rank exists,
        # and if it does exist it is maintained
        if rank_diff == 0:
            delta = 1 if file_diff < 0 else -1
            edge = -1 if delta < 0 else 8

            # Is there an empty path between us and the king?
            for i in range(king_pos.file + delta, self.pos.file, delta):
                pos = Pos(rank=self.pos.rank, file=i)
                piece = board.get(pos)
                
                # If the piece is not empty, return True because there is no pin to maintain
                if piece is not None:
                    return True
      
            # Is there a piece pinning us to the king?
            for i in range(self.pos.file + delta, edge, delta):
                pos = Pos(rank=self.pos.rank, file=i)
                piece = board.get(pos)

                # If we encounter a piece
                if piece is not None:
                    # And the piece is not the current player's piece
                    if piece.player is not board.current_player:
                        # And the piece can pin orthogonally (it is a rook or queen)
                        if piece.can_pin_orthogonally():
                            # And the destination does not stay on this rank
                            if dest.rank != self.pos.rank:
                                # Then the pin is not maintained
                                return False
                    # Once we have found a piece that does not return False to the above condition
                    # we no longer need to iterate along the file
                    break 
        
        # If the piece is on the same file as the King we must check if any pin along the file exists, 
        # and if it does exist it is maintained
        if file_diff == 0:
            delta = 1 if rank_diff < 0 else -1
            edge = -1 if delta < 0 else 8

            for i in range(king_pos.rank + delta, self.pos.rank, delta):
                pos = Pos(rank=i, file=self.pos.file)
                piece = board.get(pos)

                if piece is not None:
                    return True
    
            for i in range(self.pos.rank + delta, edge, delta):
                pos = Pos(rank=i, file=self.pos.file)
                piece = board.get(pos)

                if piece is not None:
                    if piece.player is not board.current_player:
                        if piece.can_pin_orthogonally():
                            if self.pos.file != dest.file:
                                return False
                    break 
        
        # Avoid division by zero
        if rank_diff == 0 or file_diff == 0:
            return True

        # If the piece is on the same diagonal as the King we must check if any pin along the diagonal
        # exists, and if it does exist it is maintained
        if abs(rank_diff/file_diff) == 1:
            delta_rank = 1 if rank_diff < 0 else -1
            delta_file = 1 if file_diff < 0 else -1

            # As we search for a pinning piece keep track of the possible moves we could have made that 
            # would maintain the pin 
            possible_moves = []

            # Is there an empty path between us and the king?
            for rank, file in zip(range(king_pos.rank+delta_rank, self.pos.rank, delta_rank),\
                        range(king_pos.file+delta_file, self.pos.file, delta_file)):
                pos = Pos(rank, file)
                possible_moves.append(pos)
                piece = board.get(pos)

                # If the piece is not empty, return True because there is no pin to maintain
                if piece is not None:
                    return True

            # How many tiles are between the current piece and the edge of the board along the piece-King
            # diagonal?
            num_steps = min(7 - self.pos.rank if delta_rank > 0 else self.pos.rank, \
                            7 - self.pos.file if delta_file > 0 else self.pos.file)
            
            edge_rank = self.pos.rank + delta_rank * num_steps
            edge_file = self.pos.file + delta_file * num_steps

            for i, j in zip(range(self.pos.rank + delta_rank, edge_rank, delta_rank), \
                            range(self.pos.file + delta_file, edge_file, delta_file)):
                pos = Pos(rank=i, file=j)
                possible_moves.append(pos)
                piece = board.get(pos)
                if piece is not None:
                    if piece.can_pin_diagonally():
                        if dest not in possible_moves:
                            return False
                    break 
        
        return True

    @abc.abstractstaticmethod
    def get_origin(destination_pos: Pos, board, origin_hint: str = None) -> Pos:
        """
        Determine the origin position of a piece given its destination.

        param destination_pos:
            The position the piece is attempting to move
        param board:
            The current state of the board
        param origin_hint: 
            A string used to give additional information about the location of the piece. For 
            example in the string Bad4, "a" is a hint describing the location of the bishop on
            the a-file.

        return:
            The origin position
        """
        raise NotImplementedError

    @staticmethod
    def get_hint_origin(origin_hint: str, piece_type: Type[Piece], board) -> Pos:
        # TODO: method description
        """
        """
        if len(origin_hint) == 2:
            return Pos.index(origin_hint)
        elif origin_hint.isnumeric():
            rank = int(origin_hint) - 1
            for file in range(8):
                pos = Pos(rank, file)
                if isinstance(board.get(pos), piece_type) and \
                        board.get(pos).player == board.current_player:
                    return pos
        else:
            file = Pos.index_from_file(origin_hint)
            for rank in range(8):
                pos = Pos(rank, file)
                if isinstance(board.get(pos), piece_type) and \
                        board.get(pos).player == board.current_player:
                    return pos
        raise PieceNotFoundException()

    @abc.abstractmethod
    def __copy__(self):
        raise NotImplementedError
