from enum import Enum


class Move(Enum):
    CAPTURE = 0
    MOVE = 1
    ILLEGAL = 2
    
    def is_legal(self) -> bool:
        return not self is Move.ILLEGAL

    def is_capture(self) -> bool:
        return self is Move.CAPTURE
            