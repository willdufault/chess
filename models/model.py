from models.engine import Engine
from models.bot import Bot
from models.board import Board
from typing import Tuple

class Model:
    def __init__(self, depth: int):
        self.board = Board()
        self.engine = Engine()
        self.bot = Bot(depth, self.engine)
        self.move_count = 0

    def validMove(self, move: Tuple[int]) -> bool:
        """
        Determines if move is formatted correctly. To be correctly formatted, it
        must (1) have a length of 4, (2) contain only 1-digit integers, and (3) 
        have the second half be different than the first half. 
        """
        return len(move) == 4 and all([(x < 9) for x in move]) \
            and move[:2] != move[2:]
    
    def legalMove(self, move: Tuple[int]) -> bool:
        """
        Given a valid move, determines if the move is legal.
        """
        r, c, rx, cx = move
        return (r, c, rx, cx) in self.board.legal_moves
    
    def updateMoveCount(self) -> None:
        """
        Increment the move count.
        """
        self.move_count += 1