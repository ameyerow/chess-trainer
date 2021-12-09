from typing import NamedTuple
from .player import Player

file_map = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
rev_file_map = {0:"a",1:"b",2:"c",3:"d",4:"e",5:"f",6:"g",7:"h"}


class Pos(NamedTuple):
    rank: int
    file: int

    @staticmethod
    def index(coord, player=Player.WHITE):
        # TODO: fill in param description for player
        """
        param coord: 
            A string representing the classic pgn coordinates, i.e. d4
        param player:

        return: 
            an int which is the index in a 1D array corresponding to the pgn
            coordinate
        """
        rank = int(coord[1])-1 if player == Player.WHITE else 8-int(coord[1])
        file = file_map[coord[0]]
        
        return Pos(rank, file)
    
    @staticmethod
    def index_from_file(file: str) -> int:
        return file_map[file]

    @staticmethod
    def file_from_index(index: int) -> str:
        return rev_file_map[index]