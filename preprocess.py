import re
from model import *
from enum import Enum
from collections import defaultdict

def state_map_from_pgn(filepath, state_map=None):
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
            variation_states.append(variation_states[-1].copy())
        elif overall == ")":
            # Exiting a variation, pop the current states of the top of the stack and return to 
            # the state we were in before starting the variation
            variation_states.pop()
        else:
            first_move = match.group(1)
            second_move = match.group(2)

            if overall.startswith("1. "): 
                # Started a new pgn chapter, add the initial state to the stack
                variation_states.append(StatePair(black_moved=State(State.STARTING_STATE)))
            
            if "..." in overall:
                # This indicates white has moved and it is currently black's turn
                key, val = variation_states[-1].make_move(Players.BLACK, first_move)
                state_map[str(key)].add(str(val))
            else:
                # It is white's turn to move
                key, val = variation_states[-1].make_move(Players.WHITE, first_move)
                state_map[str(key)].add(str(val))

                if second_move is None: 
                    continue

                key, val = variation_states[-1].make_move(Players.BLACK, second_move)
                state_map[str(key)].add(str(val))

    return state_map

            
    

        
        
        