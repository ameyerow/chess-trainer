import re
from typing import Set
from .model.board import *
from .model.player import Player
from collections import defaultdict


class StateNode():
    def __init__(self, move: str, state: str, comment: str = "", depth: int = None):
        self.move = move
        self.state = state
        self.comment = comment
        self.depth = depth

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, StateNode)and self.move == __o.move and self.state == __o.state

    def __ne__(self, __o: object) -> bool:
        return not (self == __o)

    def __hash__(self) -> int:
        return hash((self.move, self.state))

class StatePair():
    def __init__(self, white_moved=None, black_moved=None):
        self.white_moved = white_moved
        self.black_moved = black_moved

    def copy(self):
        newstate = StatePair(
            white_moved=copy(self.white_moved),
            black_moved=copy(self.black_moved))
        return newstate

    def make_move(self, player, move):
        """
        param player: 
            white or black
        param move: 
            the move string, i.e. "1. d4 d5"
        return: 
            a tuple of the form (old_state, updated_state)
        """
        if player is Player.WHITE:
            self.white_moved = self.black_moved.update(move)
            return self.black_moved, self.white_moved
        elif player is Player.BLACK:
            self.black_moved = self.white_moved.update(move)
            return self.white_moved, self.black_moved   

def state_map_from_pgn(filepath, state_map: Dict[str, Set[StateNode]] = None):
    if state_map is None:
        state_map = defaultdict(set)

    pattern_header = "(\[[^\[]*\])"
    # pattern_comment = "(\{[^\}]*\})"
    pattern_exclamation = "(\$\d+)"
    # pattern_move_and_variation = "(?:\d+\.+\s*((?:(?:[PNBRQK](?:[a-h]|[1-8])?)?[a-h][1-8]|O(?:-?O"\
    #                              "){1,2}|(?:[PNBRQK](?:[a-h]|[1-8])?|[a-h])x[a-h][1-8])(?:=[NBRQ]"\
    #                              ")?[\+#]?)\s*((?:(?:[PNBRQK](?:[a-h]|[1-8])?)?[a-h][1-8]|O(?:-?O"\
    #                              "){1,2}|(?:[PNBRQK](?:[a-h]|[1-8])?|[a-h])x[a-h][1-8])(?:=[NBRQ]"\
    #                              ")?[\+#]?)?)|\(|\)"
    pattern_move_comment_variation = "(?:\s*(\{[^\}]*\})?\s*(\d+\.+)\s*((?:(?:[PNBRQK](?:[a-h]|"\
                                         "[1-8])?)?[a-h][1-8]|O(?:-?O){1,2}|(?:[PNBRQK](?:[a-h]|["\
                                         "1-8])?|[a-h])x[a-h][1-8])(?:=[NBRQ])?[\+#]?)\s*(\{[^\}]"\
                                         "*\})?\s*((?:(?:[PNBRQK](?:[a-h]|[1-8])?)?[a-h][1-8]|O(?"\
                                         ":-?O){1,2}|(?:[PNBRQK](?:[a-h]|[1-8])?|[a-h])x[a-h][1-8"\
                                         "])(?:=[NBRQ])?[\+#]?)?)\s*(\{[^\}]*\})?|\(|\)"

    with open(filepath) as f:
        pgn = f.read().replace("\n", " ")
        f.close()
    
    # Remove comments, exclamations, and headers from the pgn
    pgn_pruned = re.sub(pattern_header, '', pgn)
    pgn_pruned = re.sub(pattern_exclamation, '', pgn_pruned)

    # Each StatePair element in the stack contains the board States after the white and black moves
    variation_states = []

    for match in re.finditer(pattern_move_comment_variation, pgn_pruned):
        overall = match.group(0)

        if overall == "(":
            # Entering a variation, push the current white and black states to the stack so we 
            # can go back to our current state after we are done with the variation
            variation_states.append(copy(variation_states[-1]))
        elif overall == ")":
            # Exiting a variation, pop the current states of the top of the stack and return to 
            # the state we were in before starting the variation
            variation_states.pop()
        else:
            move_number = match.group(2)
            first_move = match.group(3)
            first_move_comment = match.group(4) if match.group(4) is not None else ""
            second_move = match.group(5)
            second_move_comment = match.group(6) if match.group(6) is not None else ""

            if move_number == "1.": 
                # Started a new pgn chapter, add the initial state to the stack
                variation_states.append(StatePair(black_moved=Board()))
            
            if "..." in move_number:
                # This indicates white has moved and it is currently black's turn
                key, val = variation_states[-1].make_move(Player.BLACK, first_move)
                state_map[str(key)].add(StateNode(first_move, str(val), comment=first_move_comment))
            else:
                # It is white's turn to move
                key, val = variation_states[-1].make_move(Player.WHITE, first_move)
                state_map[str(key)].add(StateNode(first_move, str(val), comment=first_move_comment))

                if second_move is None: 
                    continue

                key, val = variation_states[-1].make_move(Player.BLACK, second_move)
                state_map[str(key)].add(StateNode(second_move, str(val), comment=second_move_comment))

    # Third element of each tuple in the continuations should be the greatest depth in that variation.
    states_to_compute: List[StateNode] = list(state_map[str(Board())])
    finished_states = 0
    
    while states_to_compute:
        curr_node = states_to_compute[-1]

        if curr_node.depth is not None:
            states_to_compute.pop()
            finished_states = finished_states + 1
            continue

        possible_continuations = state_map[curr_node.state]
        if not possible_continuations:
            curr_node.depth = 1
            states_to_compute.pop()
            finished_states = finished_states + 1
            continue
        
        depths = []
        found_none = False
        for node in possible_continuations:
            node: StateNode = node
            if node.depth is None:
                if node in states_to_compute:
                    node.depth = 1
                else:
                    found_none = True
                    states_to_compute.append(node)
            depths.append(node.depth)

        if not found_none:
            curr_node.depth = max(depths) + 1
            states_to_compute.pop()
            finished_states = finished_states + 1

    return state_map
        