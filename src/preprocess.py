import re
from typing import Set
from .model.board import *
from .model.player import Player
from collections import defaultdict

class StateNode():
    def __init__(self, move: str, state: str, depth: int = None):
        self.move = move
        self.state = state
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
    pattern_comment = "(\{[^\}]*\})"
    pattern_exclamation = "(\$\d+)"
    pattern_move_and_variation = "(?:\d+\.+\s*((?:(?:[PNBRQK](?:[a-h]|[1-8])?)?[a-h][1-8]|O(?:-?O"\
                                 "){1,2}|(?:[PNBRQK](?:[a-h]|[1-8])?|[a-h])x[a-h][1-8])(?:=[NBRQ]"\
                                 ")?[\+#]?)\s*((?:(?:[PNBRQK](?:[a-h]|[1-8])?)?[a-h][1-8]|O(?:-?O"\
                                 "){1,2}|(?:[PNBRQK](?:[a-h]|[1-8])?|[a-h])x[a-h][1-8])(?:=[NBRQ]"\
                                 ")?[\+#]?)?)|\(|\)"

    with open(filepath) as f:
        pgn = f.read().replace("\n", " ")
        f.close()
    
    # Remove comments, exclamations, and headers from the pgn
    pgn_pruned = re.sub(pattern_header, '', pgn)
    pgn_pruned = re.sub(pattern_comment, '', pgn_pruned)
    pgn_pruned = re.sub(pattern_exclamation, '', pgn_pruned)

    # Each StatePair element in the stack contains the board States after the white and black moves
    variation_states = []

    for match in re.finditer(pattern_move_and_variation, pgn_pruned):
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
            first_move = match.group(1)
            second_move = match.group(2)

            if overall.startswith("1. "): 
                # Started a new pgn chapter, add the initial state to the stack
                variation_states.append(StatePair(black_moved=Board()))
            
            if "..." in overall:
                # This indicates white has moved and it is currently black's turn
                key, val = variation_states[-1].make_move(Player.BLACK, first_move)
                
                # Check for draws
                # If a repetition is found, do not add this edge
                state_map[str(key)].add(StateNode(first_move, str(val)))
            else:
                # It is white's turn to move
                key, val = variation_states[-1].make_move(Player.WHITE, first_move)
                state_map[str(key)].add(StateNode(first_move, str(val)))

                if second_move is None: 
                    continue

                key, val = variation_states[-1].make_move(Player.BLACK, second_move)
                state_map[str(key)].add(StateNode(second_move, str(val)))

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
        