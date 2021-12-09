import os
from .controller import *
from .preprocess import *

def main():
    pgn_path = os.path.join(os.getcwd(), "pgns/d4Dynamite.pgn")
    state_map = state_map_from_pgn(pgn_path)

    print()

    display_board(state_map)

if __name__ == "__main__":
    main()






                 