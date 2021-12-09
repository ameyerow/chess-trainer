class PieceNotFoundException(Exception):
    def __init__(self, 
                message="Piece not found"):
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        output = self.message
        return output

class PieceTypeDoesNotExistException(Exception):
    def __init__(self,
                message="Piece type does not exist"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        output = self.message
        return output