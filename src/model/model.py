import re
import itertools
from enum import Enum

class Players(Enum):
    WHITE = 0
    BLACK = 7
    def flip(self):
        if self == Players.WHITE:
            return Players.BLACK
        else:
            return Players.WHITE

class Pieces(Enum):
    E = 0 # Empty
    P = 1 # Pawn
    N = 2 # Knight
    B = 3 # Bishop
    R = 4 # Rook
    Q = 5 # Queen
    K = 6 # King
    EP = 7 # Pawn (that is able to be captured En Passant)

class PieceNotFoundException(Exception):
    def __init__(self, state_arr, player, dest, piece, hint=None, message="Piece not found"):
        self.state_arr = state_arr
        self.player = player
        self.dest = dest
        self.piece = piece
        self.message = message
        self.hint = hint
        super().__init__(self.message)
    
    def __str__(self):
        output = self.message + "\n\n" + \
            ("Black's move:\n" if self.player == Players.BLACK else "White's move:\n") + \
            self.piece.name + " to " + self.dest + "\n\n"  
        for i in range(8):
            for j in range(8):
                idx = 8 * i + j
                output = output + str(self.state_arr[idx])
            output = output + "\n"

        return output

class StatePair():
    def __init__(self, white_moved=None, black_moved=None):
        self.white_moved = white_moved
        self.black_moved = black_moved

    def copy(self):
        newstate = StatePair(white_moved=self.white_moved.copy(), \
            black_moved=self.black_moved.copy())
        return newstate

    def __str__(self):
        output = ""
        for i in range(8):
            for j in range(8):
                idx = 8 * i + j
                output = output + ('0' if self.white_moved is None else self.white_moved[idx])
            output = output + "\n"
        output = output + "\n"

        for i in range(8):
            for j in range(8):
                idx = 8 * i + j
                output = output + ('0' if self.black_moved is None else self.black_moved[idx])
            output = output + "\n"
        output = output + "\n"

        return output

    def make_move(self, player, move):
        """
        param player: 
            white or black
        param move: 
            the move string, i.e. "1. d4 d5"
        return: 
            a tuple of the form (old_state, updated_state)
        """
        if player == Players.WHITE:
            self.white_moved = self.black_moved.update(move)
            return self.black_moved, self.white_moved
        elif player == Players.BLACK:
            self.black_moved = self.white_moved.update(move)
            return self.white_moved, self.black_moved   
    
class State():
    STARTING_STATE = list("42356324111111110000000000000000000000000000000088888888b9acda9b"
                          "000" # These three bits determine if Ra, K, Rh have moved for white
                          "000" # These three bits determine if Ra, K, Rh have moved for black
                          "00"  # Are the white and black kings in check? 
                          "0")  # Bit to determine which player's turn it is

    def __init__(self, state):
        self.state = state
        self.file_map = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
        self.rev_file_map = {0:"a",1:"b",2:"c",3:"d",4:"e",5:"f",6:"g",7:"h"}

    def copy(self):
        newstate = State(self.state.copy())
        return newstate

    def __str__(self):
        output = ""
        for el in self.state:
            output = output + el
        return output   

    def is_under_attack(self, pos):
        """
        param pos: 
            a (rank, file) position
        return:
            whether or not the pos is under attack by another piece
        """
        
        pass

    def legal_moves(self, pos):
        """
        param pos: 
            the (rank, file) position of the piece being moved
        return:
            a list of legal moves for the current piece
        """
        # TODO: speed this up
        moves = []
        captures = []
        for i in range(8):
            for j in range(8):
                legal, is_a_capture = self.is_legal_move(pos, (i, j))
                if legal and is_a_capture:
                    captures.append((i, j))
                elif legal:
                    moves.append((i, j))
        return moves, captures

    def is_legal_move(self, pos, dest):
        """
        param pos:
            the (rank, file) position of the piece being moved
        param dest:
            the (rank, file) position of the destination tile
        return:
            whether or not the move is legal and whether the move is capture
        """
        # If pos and dest are the same it is not a legal move
        if pos == dest:
            return False, False

        player_turn = Players(int(self.state[-1]))
        idx = 8*pos[0]+pos[1]
        el = int(self.state[idx], 16)

        # If the piece is empty this can not be a legal move
        if el == Pieces.E.value:
            return False, False

        player = Players.BLACK if el > Players.BLACK.value else Players.WHITE

        # If the piece selected is not the current player's piece then this is not
        # a legal move
        if player_turn != player:
            return False, False
        
        # Retrieve the type of piece that the player is attempting to move
        piece = Pieces(el - player.value)

        idx = 8 * dest[0] + dest[1]
        dest_is_empty = int(self.state[idx], 16) == Pieces.E.value

        # A piece is capturable if is not owned by the current player
        if player == player.BLACK:
            dest_is_capturable_piece = 0 < int(self.state[idx], 16) <= Players.BLACK.value
        else:
            dest_is_capturable_piece = int(self.state[idx], 16) > Players.BLACK.value

        legal_move = (dest_is_empty or dest_is_capturable_piece)

        # Shortcircuit to avoid computation
        if not legal_move:
            return False, False

        rank_diff = dest[0] - pos[0] 
        file_diff = dest[1] - pos[1]

        clear_path = True
        correct_move_shape = False

        if piece == Pieces.K:
            # TODO
            # Castling: king can't pass through check, the appropriate castling state bits must
            # be 0, and path between rook and king must be empty
            flip = player == Players.BLACK
            player_offset = 0 if player == Players.WHITE else 3
            if idx == self.index("g1", flip=flip):
                # Short castle
                path_is_empty = \
                    self.state[self.index("f1", flip=flip)] == format(Pieces.E.value, 'x') and \
                    self.state[self.index("g1", flip=flip)] == format(Pieces.E.value, 'x')
                pieces_havent_moved = \
                    self.state[65+player_offset] == "0" and \
                    self.state[66+player_offset] == "0"

                return path_is_empty and pieces_havent_moved, False
            elif idx == self.index("c1", flip=flip):
                # Long castle
                path_is_empty = \
                    self.state[self.index("d1", flip=flip)] == format(Pieces.E.value, 'x') and \
                    self.state[self.index("c1", flip=flip)] == format(Pieces.E.value, 'x') and \
                    self.state[self.index("b1", flip=flip)] == format(Pieces.E.value, 'x')
                pieces_havent_moved = \
                    self.state[65+player_offset] == "0" and \
                    self.state[64+player_offset] == "0"

                return path_is_empty and pieces_havent_moved, False
            else:
                pass

            return False, False
        elif piece == Pieces.R:
            clear_path, correct_move_shape =\
                 self.is_legal_rook_move(rank_diff, file_diff, pos, dest)
        elif piece == Pieces.B:
            clear_path, correct_move_shape = \
                self.is_legal_bishop_move(rank_diff, file_diff, pos, dest)
        elif piece == Pieces.Q:
            clear_path, correct_move_shape = \
                self.is_legal_queen_move(rank_diff, file_diff, pos, dest)
        elif piece == Pieces.N:
            clear_path, correct_move_shape = \
                self.is_legal_knight_move(rank_diff, file_diff)
        elif piece == Pieces.P or piece == Pieces.EP:
            clear_path, correct_move_shape = \
                self.is_legal_pawn_move(rank_diff, file_diff, pos, dest, \
                    dest_is_capturable_piece, player)

        legal_move = legal_move and clear_path and correct_move_shape

        # Shortcircuit to avoid computation
        if not legal_move:
            return False, False

        # TODO: Check if move would put the King illegally in check
        # Determine if there is a straight line between the current position of our piece and the
        # King. If there is such a straight line (or diagonal) see if there is a piece that attacks
        # our piece from that line. If this is the case the we aren't allowed to move out of that
        # attack (off that straight or diagonal).
 
        king_idx = self.state.index(format(Pieces.K.value + player.value, 'x'))
        king_rank = king_idx // 8
        king_file = king_idx % 8

        rank_diff = king_rank - pos[0] 
        file_diff = king_file - pos[1]

        destination_maintains_pin = True

        is_line_to_king = rank_diff == 0 or file_diff == 0 or abs(rank_diff / file_diff) == 1

        if is_line_to_king:
            if rank_diff == 0:
                delta = 1 if file_diff < 0 else -1
                edge = -1 if delta < 0 else 8
                # Is the first non empty piece we see in this direction a queen or a rook
                for i in range(pos[1]+delta, edge, delta):
                    el = int(self.state[8 * pos[0] + i], 16)
                    if el != Pieces.E.value:
                        if el == Pieces.R.value + player.flip().value or \
                            el == Pieces.Q.value + player.flip().value:
                            if pos[0] != dest[0]:
                                destination_maintains_pin = False
                        break 
            elif file_diff == 0:
                delta = 1 if rank_diff < 0 else -1
                edge = -1 if delta < 0 else 8
                # Is the first non empty piece we see in this direction a queen or a rook
                for i in range(pos[0]+delta, edge, delta):
                    el = int(self.state[8 * i + pos[1]], 16)
                    if el != Pieces.E.value:
                        if el == Pieces.R.value + player.flip().value or \
                            el == Pieces.Q.value + player.flip().value:
                            if pos[1] != dest[1]:
                                destination_maintains_pin = False
                        break 
            else:
                # Is the first non empty piece we see in this direction a queen or a bishop

                # TODO: didn't work on left diagonal toward black king
                delta_0 = 1 if rank_diff < 0 else -1
                delta_1 = 1 if file_diff < 0 else -1

                num_steps = min(7 - pos[0] if delta_0 > 0 else pos[0], \
                    7 - pos[1] if delta_1 > 0 else pos[1])
                
                edge_0 = pos[0] + delta_0 * num_steps
                edge_1 = pos[1] + delta_1 * num_steps

                possible_moves = []
                for i, j in zip(range(pos[0]+delta_0, edge_0, delta_0), \
                                range(pos[1]+delta_1, edge_1, delta_1)):
                    possible_moves.append((i,j))
                    el = int(self.state[8 * i + j], 16)
                    if el != Pieces.E.value:
                        if el == Pieces.B.value + player.flip().value or \
                            el == Pieces.Q.value + player.flip().value:
                            if not (dest in possible_moves):
                                destination_maintains_pin = False
                        break 

        # TODO: If the king is in check, the move must address this if possible

        legal_move = legal_move and destination_maintains_pin

        return legal_move, dest_is_capturable_piece

    def is_legal_rook_move(self, rank_diff, file_diff, pos, dest):
        """
        param rank_diff: 
            the difference in rank between pos and dest
        param file_diff:
            the difference in file between pos and dest
        param pos:
            the (rank, file) position of the piece being moved
        param dest:
            the (rank, file) position of the destination tile
        return:
            whether or not the rook move is legal
        """
        # The rook can only move along either a rank or file
        clear_path = True
        correct_move_shape = rank_diff == 0 or file_diff == 0
        if correct_move_shape:
            # The path between pos and dest has to be empty
            if rank_diff == 0:
                delta = 1 if file_diff > 0 else -1
                for i in range(pos[1]+delta, dest[1], delta):
                    if int(self.state[8 * pos[0] + i], 16) != Pieces.E.value:
                        clear_path = False
            elif file_diff == 0:
                delta = 1 if rank_diff > 0 else -1
                for i in range(pos[0]+delta, dest[0], delta):
                    if int(self.state[8 * i + pos[1]], 16) != Pieces.E.value:
                        clear_path = False
        return clear_path, correct_move_shape

    def is_legal_bishop_move(self, rank_diff, file_diff, pos, dest):
        """
        param rank_diff: 
            the difference in rank between pos and dest
        param file_diff:
            the difference in file between pos and dest
        param pos:
            the (rank, file) position of the piece being moved
        param dest:
            the (rank, file) position of the destination tile
        return:
            whether or not the bishop move is legal
        """
        # The slope of the move has to be 1, a diagonal from the current location
        clear_path = True
        correct_move_shape = rank_diff != 0 and file_diff != 0 and abs(rank_diff / file_diff) == 1
        if correct_move_shape:
            # The path between pos and dest has to be empty
            delta_0 = 1 if rank_diff > 0 else -1
            delta_1 = 1 if file_diff > 0 else -1
            for i, j in zip(range(pos[0]+delta_0, dest[0], delta_0), \
                            range(pos[1]+delta_1, dest[1], delta_1)):
                if int(self.state[8 * i + j], 16) != Pieces.E.value:
                    clear_path = False

        return clear_path, correct_move_shape

    def is_legal_knight_move(self, rank_diff, file_diff):
        """
        param rank_diff: 
            the difference in rank between pos and dest
        param file_diff:
            the difference in file between pos and dest
        return:
            whether or not the knight move is legal
        """
        # The knight must move in an L shape, always has a clear path
        shape = (abs(rank_diff), abs(file_diff))
        correct_move_shape = shape == (1, 2) or shape == (2, 1)
        return True, correct_move_shape

    def is_legal_queen_move(self, rank_diff, file_diff, pos, dest):
        """
        param rank_diff: 
            the difference in rank between pos and dest
        param file_diff:
            the difference in file between pos and dest
        param pos:
            the (rank, file) position of the piece being moved
        param dest:
            the (rank, file) position of the destination tile
        return:
            whether or not the queen move is legal
        """
        # Combination of rook and bishop checks
        clear_path_B, correct_move_shape_B = self.is_legal_bishop_move(rank_diff, file_diff, pos, dest)
        clear_path_R, correct_move_shape_R = self.is_legal_rook_move(rank_diff, file_diff, pos, dest)

        if clear_path_B and correct_move_shape_B:
            return True, True
        elif clear_path_R and correct_move_shape_R:
            return True, True
        else:
            return False, False

    def is_legal_pawn_move(self, rank_diff, file_diff, pos, dest, dest_is_capturable_piece, player):
        """
        param rank_diff: 
            the difference in rank between pos and dest
        param file_diff:
            the difference in file between pos and dest
        param pos:
            the (rank, file) position of the piece being moved
        param dest:
            the (rank, file) position of the destination tile
        param dest_is_capturable_piece:
            whether or not the the destination tile is a capturable piece
        param player:
            the player who owns the pawn being moved
        return: 
            whether or not the pawn move is legal
        """
        clear_path = True
        correct_move_shape = False
        # The 'forward' direction is dependent on which player's pawn it is)
        forward_delta = 1 if player == Players.WHITE else -1

        forward1_path_idx = 8 * (pos[0]+forward_delta) + pos[1]
        forward1_path = int(self.state[forward1_path_idx], 16)
        forward2_path_idx = 8 * (pos[0]+2*forward_delta) + pos[1]
        forward2_path = int(self.state[forward2_path_idx], 16)

        if rank_diff == forward_delta and file_diff == 0 and forward1_path == Pieces.E.value:
            # A normal pawn move, forward one square
            correct_move_shape = True
        elif rank_diff == 2 * forward_delta and file_diff == 0 and forward1_path == 0 and forward2_path == Pieces.E.value:
            # If a pawn is on its starting rank it can move forward two squares 
            correct_move_shape = pos[0] == player.value + forward_delta
        elif rank_diff == forward_delta and abs(file_diff) == 1:
            # A pawn capture is possible if the destination is capturable or the pawn at its
            # shoulder is capturable en passant
            en_passant_idx = 8 * pos[0] + dest[1]
            shoulder_pawn_is_en_passant = \
                int(self.state[en_passant_idx], 16) - player.flip().value == Pieces.EP.value
            correct_move_shape = dest_is_capturable_piece or shoulder_pawn_is_en_passant
        return clear_path, correct_move_shape

    def move_to_pgn_notation(self, pos, dest):
        """
        param pos:
            the (rank, file) position of the piece being moved
        param dest:
            the (rank, file) position of the destination tile
        return:
            a pgn format of the move expressed by pos -> dest, i.e. Qa4, Rxd4
        """
        # TODO: checks and promotions and mate

        move_string = ""

        player = Players(int(self.state[-1]))

        idx_pos = 8*pos[0]+pos[1]
        el = int(self.state[idx_pos], 16)
        piece = Pieces(el - player.value)

        idx_dest = 8*dest[0]+dest[1]
        dest_is_empty = int(self.state[idx_dest], 16) == Pieces.E.value

        if player == player.BLACK:
            dest_is_capturable_piece = int(self.state[idx_dest], 16) <= Players.BLACK.value
        else:
            dest_is_capturable_piece = int(self.state[idx_dest], 16) > Players.BLACK.value

        flip = player == Players.BLACK
        if piece == Pieces.K and idx_pos == self.index("e1", flip=flip):
            if idx_dest == self.index("g1", flip=flip):
                # TODO: Temporary
                return "O-O"
                #move_string = "O-O"
            elif idx_dest == self.index("g1", flip=flip):
                # TODO: Temporary
                return "O-O-O"
                #move_string = "O-O"
        
        if piece == Pieces.P or piece == Pieces.EP:
            file_diff = dest[1] - pos[1]
            if abs(file_diff) == 1:
                # A pawn capture
                move_string = self.rev_file_map[pos[1]] + "x" + \
                    self.rev_file_map[dest[1]] + str(dest[0]+1)
            else:
                # A pawn move
                move_string = self.rev_file_map[dest[1]] + str(dest[0]+1)
            return move_string

        # If another piece of the same type could have moved to same square then the move
        # string needs a hint to correctly identify the piece. This does not apply to kings
        # and pawns
        rank_hint = ""
        file_hint = ""
        
        if piece != Pieces.P and piece != Pieces.EP and piece != Pieces.K:
            other_piece_positions = self.find_pieces_of_same_type(piece, player, pos)
            for piece_position in other_piece_positions:
                legal, _ = self.is_legal_move(piece_position, dest)
                if legal:
                    if rank_hint == "" and piece_position[1] == pos[1]:
                        rank_hint = str(pos[0] + 1)
                    elif file_hint == "" and piece_position[0] == pos[0]:
                        file_hint = self.rev_file_map[pos[1]]
                    else:
                        rank_hint = str(pos[0] + 1)
    
        move_string = move_string + piece.name + file_hint + rank_hint
        if dest_is_empty:
            move_string = move_string + self.rev_file_map[dest[1]] + str(dest[0]+1)
        elif dest_is_capturable_piece:
            move_string = move_string + "x" + self.rev_file_map[dest[1]] + str(dest[0]+1)
        return move_string
    
    def find_pieces_of_same_type(self, piece, player, pos):
        """
        param piece: 
            the piece type being looked for
        param player: 
            the player who owns the piece
        param pos: 
            the (rank, file) position of the current exemplar
        return: 
            a list of other positions that piece has been found
        """
        other_positions = []
        for i in range(8):
            for j in range(8):
                if (i, j) == pos:
                    continue
                idx = 8 * i + j
                el = int(self.state[idx], 16)
                if piece.value + player.value == el:
                    other_positions.append((i, j))
        return other_positions

    def update(self, move):
        """
        param move: 
            the move string, i.e. "Qd4"
        return: 
            the updated state
        """
        state = self.state.copy()
        player = Players(int(state[-1]))

        # TODO: can be made more efficient by only checking the ranks where En Passant pawns
        # can exist.
        # Convert all the player's En Passant pawns to normal pawns
        for i in range(64):
            if state[i] == format(Pieces.EP.value + player.value, 'x'):
                state[i] = format(Pieces.P.value + player.value, 'x')
 
        pattern = "(?:(?:([PNBRQK](?:[a-h]|[1-8])?)?([a-h][1-8])|O(?:-?O){1,2}|([PNBRQK](?:[a-h]|"\
                  "[1-8])?|[a-h])(x)([a-h][1-8]))(?:=([NBRQ]))?[\+#]?)"
        match = re.match(pattern, move)
        groups = [match.group(0), match.group(1), match.group(2), match.group(3), match.group(4), \
                  match.group(5), match.group(6)]

        if groups[0].startswith("O-O-O"):
            # Long castle
            # Note: this if statement uses .startswith instead of == because this move can also come
            # with check or result in checkmate
            flip = player == Players.BLACK
            player_offset = 0 if player == Players.WHITE else 3
            state[65+player_offset] = "1"
            state[64+player_offset] = "1" 
            state[self.index("e1", flip=flip)] = format(Pieces.E.value, 'x')
            state[self.index("a1", flip=flip)] = format(Pieces.E.value, 'x')
            state[self.index("d1", flip=flip)] = format(Pieces.R.value + player.value, 'x')
            state[self.index("c1", flip=flip)] = format(Pieces.K.value + player.value, 'x')
        elif groups[0].startswith("O-O"):
            # Short castle
            # Note: this if statement uses .startswith instead of == because this move can also come
            # with check or result in checkmate
            flip = player == Players.BLACK
            player_offset = 0 if player == Players.WHITE else 3
            state[65+player_offset] = "1"
            state[66+player_offset] = "1" 
            state[self.index("e1", flip=flip)] = format(Pieces.E.value, 'x')
            state[self.index("h1", flip=flip)] = format(Pieces.E.value, 'x')
            state[self.index("f1", flip=flip)] = format(Pieces.R.value + player.value, 'x')
            state[self.index("g1", flip=flip)] = format(Pieces.K.value + player.value, 'x')
        elif groups[3:6] == [None] * 3:
            # The move string represents moving a piece, no captures
            if groups[1] is None:
                # Moving a pawn
                origin, destination_piece = self.pawn_origin(groups[2], state, player)
                # Determine if the pawn was promoted to a different piece 
                destination_piece = destination_piece if groups[6] is None else Pieces[groups[6]]

                state[origin] = format(Pieces.E.value, 'x')
                state[self.index(groups[2])] = format(destination_piece.value + player.value, 'x')
            else:
                # Moving a piece
                origin = self.piece_origin(groups[1], groups[2], state, player)
                piece = Pieces[groups[1][0]]

                player_offset = 0 if player == Players.WHITE else 3
                flip = player == Players.BLACK

                if piece == Pieces.K:
                    state[65+player_offset] = "1"
                elif piece == Pieces.R and origin == self.index("a1", flip=flip):
                    state[64+player_offset] = "1" 
                elif piece == Pieces.R and origin == self.index("h1", flip=flip):
                    state[66+player_offset] = "1"

                state[origin] = format(Pieces.E.value, 'x')
                state[self.index(groups[2])] = format(piece.value + player.value, 'x')
        elif groups[4] == "x":
            # Capturing a piece
            if groups[3].islower():
                # Captured with a pawn
                # Determine if the pawn was promoted to a different piece 
                destination_piece = Pieces.P if groups[6] is None else Pieces[groups[6]]
                if state[self.index(groups[5])] == format(Pieces.E.value, 'x'):
                    # When a pawn captures an empty square it means it captured a pawn En Passant 
                    state[self.index(groups[5], enpassant=player)] = format(Pieces.E.value, 'x')
  
                state[self.pawn_origin(groups[5], state, player, hint=groups[3])] = format(Pieces.E.value, 'x')
                state[self.index(groups[5])] = format(destination_piece.value + player.value, 'x')
            else:
                # Captured with a piece
                origin = self.piece_origin(groups[3], groups[5], state, player)
                piece = Pieces[groups[3][0]]

                player_offset = 0 if player == Players.WHITE else 3
                flip = player == Players.BLACK

                if piece == Pieces.K:
                    state[65+player_offset] = "1"
                elif piece == Pieces.R and origin == self.index("a1", flip=flip):
                    state[64+player_offset] = "1" 
                elif piece == Pieces.R and origin == self.index("h1", flip=flip):
                    state[66+player_offset] = "1"

                state[origin] = format(Pieces.E.value, 'x')
                state[self.index(groups[5])] = format(piece.value + player.value, 'x')

        state[-1] = format(player.flip().value, 'x')

        return State(state)
    
    def piece_origin(self, piece, dest, state, player):
        """
        param piece: 
            one to three characters representing the piece type and couple character
            helping locate the position, i.e. Ra8, Rb, Q, Ng
        param dest: 
            where the piece is being moved to
        param state: 
            1D array describing the state of the board
        param player: 
            white or black
        return: 
            an int which is the index in a 1D array corresponding to the piece's
            origin position
        """
        name = piece[0]
        has_hint = len(piece) > 1

        if has_hint:
            return self.hint_origin(piece[1:] , dest, Pieces[name], state, player)
        elif Pieces[name] == Pieces.K:
            return state.index(format(Pieces.K.value + player.value, 'x'))
        elif Pieces[name] == Pieces.Q:
            return self.queen_origin(dest, state, player)
        elif Pieces[name] == Pieces.R:
            return self.rook_origin(dest, state, player)
        elif Pieces[name] == Pieces.B:
            return self.bishop_origin(dest, state, player)
        elif Pieces[name] == Pieces.N:
            return self.knight_origin(dest, state, player)
    
    def hint_origin(self, hint, dest, piece, state, player):
        """
        param hint: 
            a list of a number and letter denoting what rank and file the piece is on. It is
            possible that only one of these is present
        param piece: 
            the piece type being looked for
        param state: 
            1D array describing the state of the board
        param player: 
            white or black
        return: 
            an int which is the index in a 1D array corresponding to the knight's 
            origin position
        """
        if len(hint) == 2:
            return self.index(hint)
        elif hint.isnumeric():
            rank = int(hint) - 1
            for file in range(8):
                idx = 8 * rank + file
                if state[idx] == format(piece.value + player.value, 'x'):
                    return idx
        else:
            file = self.file_map[hint]
            for rank in range(8):
                idx = 8 * rank + file
                if state[idx] == format(piece.value + player.value, 'x'):
                    return idx
        raise PieceNotFoundException(state, player, dest, piece, hint=hint)
        
    def rook_origin(self, dest, state, player):
        """
        param dest: 
            where the rook is being moved to
        param state: 
            1D array describing the state of the board
        param player: 
            white or black
        param hint: 
            a number of letter denoting what rank or file the rook is on
        return: an int which is the index in a 1D array corresponding to the rook's
            origin position
        """
        # The rook's origin had to be on one of the straight lines from the
        # destination
        rank = int(dest[1])-1
        file = self.file_map[dest[0]]
        max_straight = max([rank, file, 7-rank, 7-file])
        for offset in range(1, max_straight+1):
            for o in [offset, -offset]:
                if 0 <= rank+o < 8:
                    idx = 8 * (rank+o) + file
                    if state[idx] == format(Pieces.R.value + player.value, 'x'):
                        return idx
                if 0 <= file+o < 8:
                    idx = 8 * rank + (file+o)
                    if state[idx] == format(Pieces.R.value + player.value, 'x'):
                        return idx
        raise PieceNotFoundException(state, player, dest, Pieces.R)
    
    def knight_origin(self, dest, state, player):
        """
        param dest: 
            where the knight is being moved to
        param state: 
            1D array describing the state of the board
        param player: 
            white or black
        param hint: 
            a number of letter denoting what rank or file the knight is on
        return: an int which is the index in a 1D array corresponding to the knight's
            origin position
        """
        rank = int(dest[1])-1
        file = self.file_map[dest[0]]
        for i, j in itertools.product([1, -1], [2, -2]):
            if 0 <= rank+i < 8 and 0 <= file+j< 8:
                idx = 8 * (rank+i) + (file+j)
                if state[idx] == format(Pieces.N.value + player.value, 'x'):
                    return idx
            if 0 <= rank+j < 8 and 0 <= file+i< 8:
                idx = 8 * (rank+j) + (file+i)
                if state[idx] == format(Pieces.N.value + player.value, 'x'):
                    return idx
        raise PieceNotFoundException(state, player, dest, Pieces.N)

    def bishop_origin(self, dest, state, player):
        """
        param dest: 
            where the bishop is being moved to
        param state: 
            1D array describing the state of the board
        param player: 
            white or black
        return: 
            an int which is the index in a 1D array corresponding to the bishop's
            origin position
        """
        # The bishop's origin had to be on one of the diagonals through the 
        # destination
        rank = int(dest[1])-1
        file = self.file_map[dest[0]]
        max_diag = max([rank, file, 7-rank, 7-file])
        for offset in range(1, max_diag+1):
            for i, j in itertools.product([offset, -offset], repeat=2):
                if 0 <= rank+i < 8 and 0 <= file+j < 8:
                    idx = 8 * (rank+i) + (file+j)
                    if state[idx] == format(Pieces.B.value + player.value, 'x'):
                        return idx
        raise PieceNotFoundException(state, player, dest, Pieces.B)

    def queen_origin(self, dest, state, player):
        """
        param dest: 
            where the queen is being moved to
        param state: 
            1D array describing the state of the board
        param player: 
            white or black
        param hint: 
            a number of letter denoting what rank or file the queen is on
        return: 
            an int which is the index in a 1D array corresponding to the queen's
            origin position
        """
        # A Queen acts as a bishop and a rook so we run the checks for those
        # two pieces
        rank = int(dest[1])-1
        file = self.file_map[dest[0]]
        max_straight = max([rank, file, 7-rank, 7-file])
        for offset in range(1, max_straight+1):
            for o in [offset, -offset]:
                if 0 <= rank+o < 8:
                    idx = 8 * (rank+o) + file
                    if state[idx] == format(Pieces.Q.value + player.value, 'x'):
                        return idx
                if 0 <= file+o < 8:
                    idx = 8 * rank + (file+o)
                    if state[idx] == format(Pieces.Q.value + player.value, 'x'):
                        return idx
        max_diag = max([rank, file, 7-rank, 7-file])
        for offset in range(1, max_diag+1):
            for i, j in itertools.product([offset, -offset], repeat=2):
                if 0 <= rank+i < 8 and 0 <= file+j < 8:
                    idx = 8 * (rank+i) + (file+j)
                    if state[idx] == format(Pieces.Q.value + player.value, 'x'):
                        return idx
        raise PieceNotFoundException(state, player, dest, Pieces.Q)
    
    def pawn_origin(self, dest, state, player, hint=None):
        """
        param dest: 
            where the pawn is being moved to
        param state: 
            1D array describing the state of the board
        param player: 
            white or black
        return: 
            an int which is the index in a 1D array corresponding to the pawn's
            origin position and the type of pawn the array index should be set to
            (either a normal pawn or an en passant pawn)
        """
        player_modifier = 1 if player == Players.WHITE else -1
        if not hint is None:
            # Hint will always be a letter indicating the file
            file = self.file_map[hint]
            rank = int(dest[1]) - 1 - player_modifier
            idx = 8 * rank + file
            if state[idx] == format(Pieces.P.value + player.value, 'x'):
                return idx
        else:
            rank = int(dest[1])-1
            file = self.file_map[dest[0]]
            one_space = 8 * (rank - player_modifier) + file
            two_space = 8 * (rank - 2*player_modifier) + file
            if state[one_space] == format(Pieces.P.value + player.value, 'x'):
                return one_space, Pieces.P
            elif state[two_space] == format(Pieces.P.value + player.value, 'x'):
                return two_space, Pieces.EP
        raise PieceNotFoundException(state, player, dest, Pieces.P)


    def index(self, coord, flip=False, enpassant=None):
        """
        param coord: 
            A string representing the classic pgn coordinates, i.e. d4
        param flip: 
            Take a coordinate on white's side of the board and flips the
            rank such that it is the mirrored coordinate on black's side of the 
            board (or visa versa)
        param enpassant:
            Used for pawn capture en passant. Given a move like "dxe6" and respective
            destination "e6" this will return "e5", the location of the pawn that has
            been captured. This should contain the color of the pawn, white or black.
        return: 
            an int which is the index in a 1D array corresponding to the pgn
            coordinate
        """
        rank = int(coord[1])-1 if not flip else 8-int(coord[1])

        if not enpassant is None:
            rank -= 1 if enpassant == Players.WHITE else -1

        file = self.file_map[coord[0]]
        idx = 8 * rank + file
        return idx