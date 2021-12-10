from __future__ import annotations

import re
from copy import copy
from typing import Dict, List, Union

from src.model import pieces

from .pos import Pos
from .move import Move
from .player import Player
from .pieces.piece import Piece
from .pieces.knight import Knight
from .pieces.bishop import Bishop
from .pieces.queen import Queen
from .pieces.king import King
from .pieces.rook import Rook
from .pieces.pawn import Pawn
from .exceptions import PieceNotFoundException, PieceTypeDoesNotExistException


class Board():
    def __init__(self, board_str: str = None):
        if board_str is None:
            self.current_player = Player.WHITE
            self.pieces: List[List[Piece]] = [
                [Rook(  Pos(0,0), Player.WHITE),    Knight( Pos(0,1), Player.WHITE), 
                Bishop(Pos(0,2), Player.WHITE),    Queen(  Pos(0,3), Player.WHITE), 
                King(  Pos(0,4), Player.WHITE),    Bishop(Pos(0,5), Player.WHITE), 
                Knight( Pos(0,6), Player.WHITE),   Rook(   Pos(0,7), Player.WHITE)],
                [Pawn(  Pos(1,0), Player.WHITE),    Pawn(   Pos(1,1), Player.WHITE),
                Pawn(  Pos(1,2), Player.WHITE),    Pawn(   Pos(1,3), Player.WHITE),
                Pawn(  Pos(1,4), Player.WHITE),    Pawn(   Pos(1,5), Player.WHITE),
                Pawn(  Pos(1,6), Player.WHITE),    Pawn(   Pos(1,7), Player.WHITE)],
                [None for _ in range(8)],
                [None for _ in range(8)],
                [None for _ in range(8)],
                [None for _ in range(8)],
                [Pawn(  Pos(6,0), Player.BLACK),    Pawn(   Pos(6,1), Player.BLACK),
                Pawn(  Pos(6,2), Player.BLACK),    Pawn(   Pos(6,3), Player.BLACK),
                Pawn(  Pos(6,4), Player.BLACK),    Pawn(   Pos(6,5), Player.BLACK),
                Pawn(  Pos(6,6), Player.BLACK),    Pawn(   Pos(6,7), Player.BLACK)],
                [Rook(  Pos(7,0), Player.BLACK),    Knight( Pos(7,1), Player.BLACK), 
                Bishop(Pos(7,2), Player.BLACK),    Queen(  Pos(7,3), Player.BLACK), 
                King(  Pos(7,4), Player.BLACK),    Bishop(Pos(7,5), Player.BLACK), 
                Knight( Pos(7,6), Player.BLACK),   Rook(   Pos(7,7), Player.BLACK)],
            ]
        else:
            self.current_player = Player.WHITE if board_str[-1] == "0" else Player.BLACK
            self.pieces = self.__init_pieces_from_board_str(board_str)
    

    def get(self, tile: Union[Pos, str], player=None) -> Piece:
        """
        Get the piece at the given position

        param tile:
            The tile you want to retrieve, either a position or a string denoting the tile position
            i.e. "d4"
        param player:
            If given the tile argument as a string, this argument allows you to mirror the given
            coordinate to a player's side of the board. For example the coordinate "h1" will be 
            mirrored to "h8" when passed in Player.BLACK.

        return:
            The piece
        """
        if isinstance(tile, str):
            pos = Pos.index(tile, player=player)
        else:
            pos = tile

        return self.pieces[pos.rank][pos.file]

    def set(self, tile: Union[Pos, str], piece: Piece, player=None):
        """
        Set the given tile to the given piece

        param tile:
            The tile you want to retrieve, either a position or a string denoting the tile position
            i.e. "d4".
        param piece: 
            The piece.
        param player:
            If given the tile argument as a string, this argument allows you to mirror the given
            coordinate to a player's side of the board. For example the coordinate "h1" will be 
            mirrored to "h8" when passed in Player.BLACK.
        """
        if isinstance(tile, str):
            pos = Pos.index(tile, player=player)
        else:
            pos = tile

        if piece is not None:
            piece.pos = pos
        self.pieces[pos.rank][pos.file] = piece

    def is_empty(self, tile: Union[Pos, str], player=None) -> bool:
        """
        Is the given tile empty?

        param tile:
            The tile you want to retrieve, either a position or a string denoting the tile position
            i.e. "d4"
        param player:
            If given the tile argument as a string, this argument allows you to mirror the given
            coordinate to a player's side of the board. For example the coordinate "h1" will be 
            mirrored to "h8" when passed in Player.BLACK.

        return:
            True if the tile is empty, False otherwise
        """
        return self.get(tile, player=player) is None

    def get_king_pos(self, player: Player) -> Pos:
        """
        Get the position of the king for the given player

        param player:
            Either WHITE or BLACK
        
        return:
            The position of the King
        """
        for rank in self.pieces:
            for piece in rank:
                if isinstance(piece, King) and piece.player == player:
                    return piece.pos
        raise PieceNotFoundException(self, message="Did not find {} king".format(
            "black" if player is Player.BLACK else "white"))

    # TODO: CRASHES IN ENGLUND GAMBIT LINE!!!
    def is_legal_move(self, dest: Pos, piece: Piece) -> Move:
        """
        Given a destination position, determine if this piece can legally move there given the
        current board state.

        param dest:
            The position the piece is attempting to move
        param board:
            The current state of the board

        return:
            True if it is a legal move, False otherwise
        """
        # If pos and dest are the same, this is an ILLEGAL move
        if piece.pos == dest:
            return Move.ILLEGAL

        # If the piece selected is not the current player's piece then this is an ILLEGAL move
        if self.current_player != piece.player:
            return Move.ILLEGAL

        # If the destination tile is occupied with the player's own piece the move is ILLEGAL
        if not self.is_empty(dest) and self.get(dest).player == piece.player:
            return Move.ILLEGAL

        # If the move shape is not correct or the path to the destination tile is blocked in some way,
        # the move is ILLEGAL
        if not piece.is_dest_reachable(dest, self):
            return Move.ILLEGAL
        
        # If the move would move a pinned piece such that the king would now be in check, the move is
        # an ILLEGAL move
        if not piece.maintains_pin(dest, self):
            return Move.ILLEGAL

        # If the king is in check, the current move must address this otherwise it is an illegal move. If
        # the piece being moved is the king, then it must move to a square that is not under attack (this is
        # already addressed by "piece.is_dest_reachable(dest, self)" above). If any other piece is being moved 
        # it must block the check (not possible if more than one piece is attacking the king), or capture the
        # checking piece.
        king_pos = self.get_king_pos(self.current_player)
        king: King = self.get(king_pos)
        if king.in_check and not isinstance(piece, King):
            attacking_piece_positions = self.is_under_attack(king_pos)
            if len(attacking_piece_positions) > 1:
                return Move.ILLEGAL

            attacking_piece = self.get(attacking_piece_positions[0])
            if dest != attacking_piece.pos and not self.__blocks_attack(dest, attacking_piece, king):
                return Move.ILLEGAL

        # If the destination square is empty the move is a MOVE, otherwise it is a capture
        if self.get(dest) is None:
            return Move.MOVE
        else:
            return Move.CAPTURE

    def __blocks_attack(self, dest: Pos, from_piece: Piece, to_piece: Piece) -> bool:
        """
        Whether or not moving a piece to the position "pos" would block an attack.

        param dest:
            The position a piece is being moved to.
        param from_piece:
            The piece that is attacking.

        param to_piece:
            The piece that is being attacked.

        return: True if the attack was blocked, False otherwise
        """
        from_pos = from_piece.pos
        to_pos = to_piece.pos
        rank_diff = from_pos.rank - to_pos.rank
        file_diff = from_pos.file - to_pos.file

        if from_piece.can_pin_orthogonally() and rank_diff == 0:
            min_file = min(from_pos.file, to_pos.file)
            max_file = max(from_pos.file, to_pos.file)
            rank = from_pos.rank # Same as to_piece.rank

            for file in range(min_file+1, max_file):
                curr_pos = Pos(rank, file)
                if curr_pos == dest:
                    return True
        elif from_piece.can_pin_orthogonally() and file_diff == 0:
            min_rank = min(from_pos.rank, to_pos.rank)
            max_rank = max(from_pos.rank, to_pos.rank)
            file = from_pos.file # Same as to_piece.file

            for rank in range(min_rank+1, max_rank):
                curr_pos = Pos(rank, file)
                if curr_pos == dest:
                    return True

        if from_piece.can_pin_diagonally():
            min_rank = min(from_pos.rank, to_pos.rank)
            max_rank = max(from_pos.rank, to_pos.rank)
            min_file = min(from_pos.file, to_pos.file)
            max_file = max(from_pos.file, to_pos.file)

            for rank, file in zip(range(min_rank+1, max_rank), range(min_file+1, max_file)):
                curr_pos = Pos(rank, file)
                if curr_pos == dest:
                    return True

        return False

    def is_under_attack(self, 
                        tile: Union[Pos, str], 
                        transparent_piece: Piece = None, 
                        player: Player = None) -> List[Pos]:
        """
        Determine which pieces, if any, are attack the given position.

        param tile:

        param transparent_piece:

        param player:
            If given the tile argument as a string, this argument allows you to mirror the given
            coordinate to a player's side of the board. For example the coordinate "h1" will be 
            mirrored to "h8" when passed in Player.BLACK.

        return:
            A list of positions, each associated with a piece that is attacking the given position.
        """
        # Ask every piece on the board if they're legally allowed to move to a square. This is how you 
        # determine if it's under attack! The current piece should be considered invisible though
        if isinstance(tile, str):
            pos = Pos.index(tile, player=player)
        else:
            pos = tile
        
        board = copy(self)
        board.current_player = board.current_player.flip()
        if transparent_piece is not None:
            board.set(transparent_piece.pos, None)

        other_player = board.current_player
        attacking_positions = []

        for rank in board.pieces:
            for piece in rank:
                if piece is None or piece.player is not other_player:
                    continue
                if piece.attacks_square_from_position(piece.pos, pos, board):
                    attacking_positions.append(piece.pos)
        return attacking_positions

    def __find_pieces_of_same_type(self, piece_type, pos) -> List[Piece]:
        """
        param piece_type: 
            the piece type being looked for
        param pos: 
            the (rank, file) position of the current exemplar

        return: 
            a list of the other pieces
        """
        pieces = []
        for i in range(8):
            for j in range(8):
                tile = Pos(rank=i, file=j)
                if Pos(rank=i, file=j) == pos:
                    continue
                piece = self.get(tile)
                if isinstance(piece, piece_type) and piece.player == self.current_player:
                    pieces.append(piece)
        return pieces

    def move_requires_promotion(self, pos: Pos, dest: Pos) -> bool:
        """
        TODO: method description
        """
        promotion_rank = 7 if self.current_player == Player.WHITE else 0
        return isinstance(self.get(pos), Pawn) and dest.rank == promotion_rank

    def get_move_destination(self, move) -> Pos:
        """
        Return the destination position of the given move.

        param move: 
            The move string, i.e. "Qd4".

        return: 
            The destination position.
        """
        player = self.current_player

        pattern = "(?:(?:([PNBRQK](?:[a-h]|[1-8])?)?([a-h][1-8])|O(?:-?O){1,2}|([PNBRQK](?:[a-h]|"\
                  "[1-8])?|[a-h])(x)([a-h][1-8]))(?:=([NBRQ]))?[\+#]?)"
        match = re.match(pattern, move)

        is_long_castle = match.group(0).startswith("O-O-O")
        is_short_castle = match.group(0).startswith("O-O")
        # Note: this if statement uses .startswith instead of == because this move can also come
        # with check or result in checkmate

        move_destination = Pos.index(match.group(2)) if match.group(2) is not None else None

        is_capture = match.group(4) is not None and match.group(4) == "x"
        capture_destination = Pos.index(match.group(5)) if match.group(5) is not None else None
        
        if is_long_castle:
            # Long castles
            castle_destination = Pos.index("c1", player = player)
            return castle_destination
        elif is_short_castle:
            # Short castles
            castle_destination = Pos.index("g1", player = player)
            return castle_destination
        elif is_capture:
            # Capturing a piece
            return capture_destination
        else:
            # The move string represents moving a piece, no captures
            return move_destination

    def get_move_origin(self, move) -> Pos:
        """
        Return the origin position of the given move.

        param move: 
            The move string, i.e. "Qd4".

        return: 
            The origin position.
        """
        player = self.current_player

        pattern = "(?:(?:([PNBRQK](?:[a-h]|[1-8])?)?([a-h][1-8])|O(?:-?O){1,2}|([PNBRQK](?:[a-h]|"\
                  "[1-8])?|[a-h])(x)([a-h][1-8]))(?:=([NBRQ]))?[\+#]?)"
        match = re.match(pattern, move)

        is_long_castle = match.group(0).startswith("O-O-O")
        is_short_castle = match.group(0).startswith("O-O")
        # Note: this if statement uses .startswith instead of == because this move can also come
        # with check or result in checkmate

        moving_piece = match.group(1)[0] if match.group(1) is not None else None
        move_origin_hint = match.group(1)[1:] if match.group(1) is not None else None
        move_destination = Pos.index(match.group(2)) if match.group(2) is not None else None

        is_capture = match.group(4) is not None and match.group(4) == "x"
        capturing_piece_or_pawn = match.group(3)[0] if match.group(3) is not None else None
        capture_origin_hint = match.group(3)[1:] if match.group(3) is not None else None
        capture_destination = Pos.index(match.group(5)) if match.group(5) is not None else None
        
        if is_long_castle or is_short_castle:
            # Castles
            king_pos = Pos.index("e1", player = player)
            return king_pos
        elif is_capture:
            # Capturing a piece
            if capturing_piece_or_pawn.islower():
                capture_origin = Pawn.get_origin(capture_destination, self, capturing_piece_or_pawn)
                return capture_origin
            else:
                # Captured with a piece
                capture_origin = self.__get_piece_origin(
                    capturing_piece_or_pawn, 
                    capture_destination, 
                    origin_hint=capture_origin_hint)
                return capture_origin
        else:
            # The move string represents moving a piece, no captures
            if moving_piece is None:
                # Moving a pawn
                move_origin = Pawn.get_origin(move_destination, self)
                return move_origin
            else:
                # Moving a piece
                move_origin = self.__get_piece_origin(
                    moving_piece, 
                    move_destination, 
                    origin_hint=move_origin_hint)
                return move_origin

    def update(self, move) -> Board:
        """
        Update the board via the given move. We assume that the move results in a legal board state.

        param move: 
            The move string, i.e. "Qd4".

        return: 
            The updated board.
        """
        print(move)
        updated_board: Board = copy(self)
        player = updated_board.current_player

        # Convert all the other player's "capturable by En Passant pawns" to normal pawns
        for i in range(8):
            fourth_rank = updated_board.get(Pos(rank=3, file=i))
            fifth_rank = updated_board.get(Pos(rank=4, file=i))
            if isinstance(fourth_rank, Pawn) and fourth_rank.player != player:
                fourth_rank.is_capturable_en_passant = False
            if isinstance(fifth_rank, Pawn) and fifth_rank.player != player:
                fifth_rank.is_capturable_en_passant = False
 
        pattern = "(?:(?:([PNBRQK](?:[a-h]|[1-8])?)?([a-h][1-8])|O(?:-?O){1,2}|([PNBRQK](?:[a-h]|"\
                  "[1-8])?|[a-h])(x)([a-h][1-8]))(?:=([NBRQ]))?[\+#]?)"
        match = re.match(pattern, move)

        is_check = match.group(0).endswith("+")
        is_long_castle = match.group(0).startswith("O-O-O")
        is_short_castle = match.group(0).startswith("O-O")
        # Note: this if statement uses .startswith instead of == because this move can also come
        # with check or result in checkmate

        moving_piece = match.group(1)[0] if match.group(1) is not None else None
        move_origin_hint = match.group(1)[1:] if match.group(1) is not None else None
        move_destination = Pos.index(match.group(2)) if match.group(2) is not None else None

        is_capture = match.group(4) is not None and match.group(4) == "x"
        capturing_piece_or_pawn = match.group(3)[0] if match.group(3) is not None else None
        capture_origin_hint = match.group(3)[1:] if match.group(3) is not None else None
        capture_destination = Pos.index(match.group(5)) if match.group(5) is not None else None

        promotion_piece = match.group(6)

        if is_long_castle:
            # Long castle
            # Specify that the king and rook have now moved
            king: King = updated_board.get("e1", player=player)
            rook: Rook = updated_board.get("a1", player=player)
            king.has_moved = True
            rook.has_moved = True

            # Move the pieces to the appropriate squares
            updated_board.set("c1", king, player=player)
            updated_board.set("d1", rook, player=player)
            updated_board.set("e1", None, player=player)
            updated_board.set("a1", None, player=player)
        elif is_short_castle:
            # Short castle
            # Specify that the king and rook have now moved
            king: King = updated_board.get("e1", player=player)
            rook: Rook = updated_board.get("h1", player=player)
            king.has_moved = True
            rook.has_moved = True

            # Move the pieces to the appropriate squares
            updated_board.set("g1", king, player=player)
            updated_board.set("f1", rook, player=player)
            updated_board.set("e1", None, player=player)
            updated_board.set("h1", None, player=player)
        elif is_capture:
            # Capturing a piece
            if capturing_piece_or_pawn.islower():
                # Captured with a pawn
                # Determine if the pawn was promoted to a different piece 
                if promotion_piece is None:
                    destination_piece = Pawn(capture_destination, player)
                else:
                    destination_piece = self.__convert_piece_str_to_type(
                        promotion_piece, 
                        capture_destination, 
                        player)

                if self.is_empty(capture_destination):
                    # When a pawn captures an empty square it means it captured a pawn En Passant 
                    capture_rank = capture_destination.rank
                    rank = capture_rank - 1 if player is Player.WHITE else capture_rank + 1
                    file = capture_destination.file

                    en_passant_pawn_pos = Pos(rank, file)
                    
                    #Since it has been captured, set the captured en passant pawn to empty
                    updated_board.set(en_passant_pawn_pos, None)    
                capture_origin = Pawn.get_origin(capture_destination, self, capturing_piece_or_pawn)
                updated_board.set(capture_origin, None)
                updated_board.set(capture_destination, destination_piece)
            else:
                # Captured with a piece
                capture_origin = self.__get_piece_origin(
                    capturing_piece_or_pawn, 
                    capture_destination, 
                    origin_hint=capture_origin_hint)
                
                piece = updated_board.get(capture_origin)
                piece.pos = capture_destination
                if isinstance(piece, King) or isinstance(piece, Rook):
                    piece.has_moved = True

                updated_board.set(capture_origin, None)
                updated_board.set(capture_destination, piece)

        else:
            # The move string represents moving a piece, no captures
            if moving_piece is None:
                # Moving a pawn
                move_origin = Pawn.get_origin(move_destination, self)

                # Determine if the pawn was moved two squares from its starting position
                rank_diff = abs(move_destination.rank - move_origin.rank)
                is_capturable_en_passant = rank_diff > 1

                # Determine if the pawn was promoted to a different piece
                if promotion_piece is not None:
                    destination_piece: Piece = self.__convert_piece_str_to_type(
                        promotion_piece, 
                        move_destination, 
                        player)
                else:
                    destination_piece = Pawn(
                        move_destination, 
                        player, 
                        is_capturable_en_passant=is_capturable_en_passant)
                
                updated_board.set(move_origin, None)
                updated_board.set(move_destination, destination_piece)
            else:
                # Moving a piece
                move_origin = self.__get_piece_origin(
                    moving_piece, 
                    move_destination, 
                    origin_hint=move_origin_hint)
                
                piece = updated_board.get(move_origin)
                piece.pos = move_destination
                if isinstance(piece, King) or isinstance(piece, Rook):
                    piece.has_moved = True

                updated_board.set(move_destination, piece)
                updated_board.set(move_origin, None)

        # Put other player's king in check if appropriate
        if is_check:
            king_pos = updated_board.get_king_pos(updated_board.current_player.flip())
            king = updated_board.get(king_pos)
            king.in_check = True

        # Remove check from your own king
        king_pos = updated_board.get_king_pos(updated_board.current_player)
        king = updated_board.get(king_pos)
        king.in_check = False

        updated_board.current_player = updated_board.current_player.flip()

        return updated_board

    def __get_piece_origin(self, piece: str, destination_pos: Pos, origin_hint: str = None) -> Pos:
        """
        Given the destination position, determine where the piece originated from.

        param piece:
            The piece type being moved.
        param destination_pos:
            The position the piece is being moved to.
        param origin_hint:
            A hint to get rid of ambiguity when multiple pieces of the same type could have moved
            to the destination square.

        return:

        """
        if origin_hint == '':
            origin_hint = None
        if piece == "B":
            return Bishop.get_origin(destination_pos, self, origin_hint=origin_hint)
        elif piece == "N":
            return Knight.get_origin(destination_pos, self, origin_hint=origin_hint)
        elif piece == "R":
            return Rook.get_origin(destination_pos, self, origin_hint=origin_hint)
        elif piece == "Q":
            return Queen.get_origin(destination_pos, self, origin_hint=origin_hint)
        elif piece == "K":
            return King.get_origin(destination_pos, self, origin_hint=origin_hint)
        else:
            raise PieceTypeDoesNotExistException()

    def __convert_piece_str_to_type(self, piece: str, pos: Pos, player: Player, 
                                    in_check: bool = False, has_moved: bool = False) -> Piece:
        """
        Given attributes of a piece return an instantiated object.

        param piece: 
            A string indicating the type of piece to create
        param pos:
            The postition the piece will reside in.
        param player:
            The owner of the piece.

        return:
            An instatiated Piece object with the given characteristics
        """
        if piece == "B":
            return Bishop(pos, player)
        elif piece == "N":
            return Knight(pos, player)
        elif piece == "R":
            return Rook(pos, player, has_moved=has_moved)
        elif piece == "Q":
            return Queen(pos, player)
        elif piece == "K":
            return King(pos, player, has_moved=has_moved, in_check=in_check)
        elif piece == "P":
            return Pawn(pos, player)
        elif piece == "G":
            return Pawn(pos, player, is_capturable_en_passant=True)
        else:
            raise PieceTypeDoesNotExistException()

    def move_to_pgn_notation(self, pos: Pos, dest: Pos, promotion_piece: str = None) -> str:
        """
        param pos:
            The position of the piece being moved.
        param dest:
            The position of the destination tile.
        param promotion_piece:
            If a pawn reached the other side of the board, this will be a string indicating
            which piece it promoted to i.e. "Q" or "N".

        return:
            A pgn format of the move expressed by pos -> dest, i.e. Qa4, Rxd4.
        """
        move_string = ""

        player = self.current_player
        piece = self.get(pos)
        
        dest_is_empty = self.is_empty(dest)
        dest_is_capturable_piece = not self.is_empty(dest) and \
            self.get(dest).player is not player

        # If another piece of the same type could have moved to same square then the move
        # string needs a hint to correctly identify the piece. This does not apply to kings
        # and pawns
        rank_hint = ""
        file_hint = ""
        if not isinstance(piece, Pawn) and not isinstance(piece, King):
            other_pieces = self.__find_pieces_of_same_type(piece.__class__, pos)
            for other_piece in other_pieces:
                move = self.is_legal_move(dest, other_piece)
                if move.is_legal():
                    if rank_hint == "" and other_piece.pos.file == pos.file:
                        rank_hint = str(pos.rank + 1)
                    elif file_hint == "" and other_piece.pos.rank == pos.rank:
                        file_hint = Pos.file_from_index(pos.file)
                    else:
                        file_hint = Pos.file_from_index(pos.file)

        move_string = move_string + piece.name + file_hint + rank_hint

        if dest_is_empty:
            move_string = move_string + Pos.file_from_index(dest.file) + str(dest.rank + 1)
        elif dest_is_capturable_piece:
            move_string = move_string + "x" + Pos.file_from_index(dest.file) + str(dest.rank + 1)

        if isinstance(piece, King) and pos == Pos.index("e1", player=player):
            if dest == Pos.index("g1", player=player):
                move_string = "O-O"
            elif dest == Pos.index("c1", player=player):
                move_string = "O-O-O"
        
        if isinstance(piece, Pawn):
            file_diff = dest.file - pos.file
            if abs(file_diff) == 1:
                # A pawn capture
                move_string = Pos.file_from_index(pos.file) + "x" + \
                    Pos.file_from_index(dest.file) + str(dest.rank+1)
            else:
                # A pawn move
                move_string = Pos.file_from_index(dest.file) + str(dest.rank + 1)

            if promotion_piece is not None:
                move_string = move_string + "=" + promotion_piece

        # Check if the current move results in a check. This can either come in the form of
        # a direct attack from the piece that was just moved or a discovered check.
        king_pos = self.get_king_pos(player.flip())
        if piece.attacks_square_from_position(dest, king_pos, self) or \
            self.__move_results_in_discovered_check(piece, dest, king_pos):
            move_string = move_string + "+"
        elif move_string == "O-O":
            # Check if short castle results in check from the rook
            rook = self.get("h1", player=player)
            if rook.attacks_square_from_position(Pos.index("f1", player=player), king_pos, self):
                move_string = move_string + "+"
        elif move_string == "O-O-O":
            # Check if long castle results in check from the rook
            rook = self.get("a1", player=player)
            if rook.attacks_square_from_position(Pos.index("d1", player=player), king_pos, self):
                move_string = move_string + "+"
        
        return move_string

    def __move_results_in_discovered_check(self, piece: Piece, dest: Pos, king_pos: Pos) -> bool:
        """
        Determine if moving the given piece to the destination position results in a check on the
        opposing king.

        param piece:
            The piece being moved (still in its original location).
        param dest:
            The position the piece is being moved to.
        param king_pos:
            The position of the opposing king.

        return:
            True if the move results in a discovered check, False otherwise.
        """
        
        piece_rank = piece.pos.rank
        piece_file = piece.pos.file

        king_rank = king_pos.rank
        king_file = king_pos.file

        rank_diff = piece_rank - king_rank
        file_diff = piece_file - king_file

        # Iterate from the king's position to the edge of the board. If an open line to an attacking
        # piece is found it is a discovered check.
        if rank_diff == 0:
            delta = 1 if file_diff > 0 else -1
            edge_of_board = 8 if delta == 1 else -1

            for file in range(king_file+delta, edge_of_board, delta):
                pos = Pos(piece_rank, file)
                if pos == dest:
                    break
                elif self.get(pos) is None or pos == piece.pos:
                    continue
                elif self.get(pos).can_pin_orthogonally() and self.get(pos).player == piece.player:
                    return True
                else:
                    break
        elif file_diff == 0: 
            delta = 1 if rank_diff > 0 else -1
            edge_of_board = 8 if delta == 1 else -1

            for rank in range(king_rank+delta, edge_of_board, delta):
                pos = Pos(rank, piece_file)
                if pos == dest:
                    break
                elif self.get(pos) is None or pos == piece.pos:
                    continue
                elif self.get(pos).can_pin_orthogonally() and self.get(pos).player == piece.player:
                    return True
                else:
                    break
        elif abs(rank_diff/file_diff) == 1:
            delta_file = 1 if file_diff > 0 else -1
            delta_rank = 1 if rank_diff > 0 else -1
            edge_of_board_file = 8 if delta_file == 1 else -1
            edge_of_board_rank = 8 if delta_rank == 1 else -1

            for rank, file in zip(range(king_rank+delta_rank, edge_of_board_rank, delta_rank), \
                                  range(king_file+delta_file, edge_of_board_file, delta_file)):
                pos = Pos(rank, file)
                if pos == dest:
                    break
                elif self.get(pos) is None or pos == piece.pos:
                    continue
                elif self.get(pos).can_pin_diagonally() and self.get(pos).player == piece.player:
                    return True
                else:
                    break

        return False
    
    def __str__(self) -> str:
        output = ""
        for rank in self.pieces:
            for piece in rank:
                if piece is not None:
                    piece_str = str(piece)
                    output = output + piece_str
                else:
                    output = output + "_"

        # These three bits determine if Ra, K, Rh have moved for white
        a1 = self.get("a1")
        a1_moved = "0"
        if not isinstance(a1, Rook) or a1.has_moved:
            a1_moved = "1"

        e1 = self.get("e1")
        e1_moved = "0"
        if not isinstance(e1, King) or e1.has_moved:
            e1_moved = "1"

        h1 = self.get("h1")
        h1_moved = "0"
        if not isinstance(h1, Rook) or h1.has_moved:
            h1_moved = "1"
        
        # These three bits determine if Ra, K, Rh have moved for black
        a8 = self.get("a8")
        a8_moved = "0"
        if not isinstance(a8, Rook) or a8.has_moved:
            a8_moved = "1"

        e8 = self.get("e8")
        e8_moved = "0"
        if not isinstance(e8, King) or e8.has_moved:
            e8_moved = "1"

        h8 = self.get("h8")
        h8_moved = "0"
        if not isinstance(h8, Rook) or h8.has_moved:
            h8_moved = "1"

        # Are the white and black kings in check? 
        white_king: King = self.get(self.get_king_pos(Player.WHITE))
        white_king_in_check = "1" if white_king.in_check else "0"

        black_king: King = self.get(self.get_king_pos(Player.BLACK))
        black_king_in_check = "1" if black_king.in_check else "0"

        # Bit to determine which player's turn it is
        current_player = "0" if self.current_player is Player.WHITE else "1"  

        output = output + a1_moved + e1_moved + h1_moved + a8_moved + e8_moved + h8_moved + \
            white_king_in_check + black_king_in_check + current_player

        return output  

    def __init_pieces_from_board_str(self, board_str: str):
        pieces: List[List[Piece]] = []

        in_check : Dict[Player : bool] = {}
        in_check[Player.WHITE] = board_str[70] == "1"
        in_check[Player.BLACK] = board_str[71] == "1"

        for rank in range(8):
            pieces_in_rank: List[Piece] = []
            for file in range(8):
                idx = 8 * rank + file
                piece_type = board_str[idx] 

                if piece_type == "_":
                    pieces_in_rank.append(None)
                    continue

                pos = Pos(rank, file)
                player = Player.WHITE if piece_type.isupper() else Player.BLACK

                if piece_type == "K":
                    has_moved = board_str[65] == "1"
                elif piece_type == "k":
                    has_moved = board_str[68] == "1"
                elif piece_type == "R":
                    a1_rook_moved = board_str[64] == "1"
                    h1_rook_moved = board_str[66] == "1"
                    if a1_rook_moved and h1_rook_moved:
                        has_moved = True
                    elif a1_rook_moved and pos != Pos.index("h1"):
                        has_moved = True
                    elif h1_rook_moved and pos != Pos.index("a1"):
                        has_moved = True
                    else:
                        has_moved = False
                elif piece_type == "r":
                    a8_rook_moved = board_str[67] == "1"
                    h8_rook_moved = board_str[69] == "1"
                    if a8_rook_moved and h8_rook_moved:
                        has_moved = True
                    elif a8_rook_moved and pos != Pos.index("h8"):
                        has_moved = True
                    elif h8_rook_moved and pos != Pos.index("a8"):
                        has_moved = True
                    else:
                        has_moved = False
                else:
                    has_moved = None

                piece = self.__convert_piece_str_to_type(piece_type.upper(), pos, player, in_check=in_check[player], has_moved=has_moved)
                pieces_in_rank.append(piece)
            pieces.append(pieces_in_rank)

        return pieces

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__init__()
        result.current_player = self.current_player
        for i in range(8):
            for j in range(8):
                result.pieces[i][j] = copy(self.pieces[i][j])
        return result

