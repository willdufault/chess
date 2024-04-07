from typing import Type
from .board import Board

class Engine:
    def __init__(self):
        # From Rustic Chess.
        self.position_scores = {
            "Pawn" : [  
                0,  0,  0,  0,  0,  0,  0,  0,
                50, 50, 50, 50, 50, 50, 50, 50,
                10, 10, 20, 30, 30, 20, 10, 10,
                5,  5, 10, 25, 25, 10,  5,  5,
                0,  0,  0, 20, 20,  0,  0,  0,
                5, -5,-10,  0,  0,-10, -5,  5,
                5, 10, 10,-20,-20, 10, 10,  5,
                0,  0,  0,  0,  0,  0,  0,  0
            ],
            'Knight' : [
                -50,-40,-30,-30,-30,-30,-40,-50,
                -40,-20,  0,  0,  0,  0,-20,-40,
                -30,  0, 10, 15, 15, 10,  0,-30,
                -30,  5, 15, 20, 20, 15,  5,-30,
                -30,  0, 15, 20, 20, 15,  0,-30,
                -30,  5, 10, 15, 15, 10,  5,-30,
                -40,-20,  0,  5,  5,  0,-20,-40,
                -50,-40,-30,-30,-30,-30,-40,-50
            ],
            'Bishop' : [
                -20,-10,-10,-10,-10,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5, 10, 10,  5,  0,-10,
                -10,  5,  5, 10, 10,  5,  5,-10,
                -10,  0, 10, 10, 10, 10,  0,-10,
                -10, 10, 10, 10, 10, 10, 10,-10,
                -10,  5,  0,  0,  0,  0,  5,-10,
                -20,-10,-10,-10,-10,-10,-10,-20
            ],
            'Rook' : [
                0,  0,  0,  0,  0,  0,  0,  0,
                5, 10, 10, 10, 10, 10, 10,  5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                0,  0,  0,  5,  5,  0,  0,  0
            ],
            'Queen' : [
                -20,-10,-10, -5, -5,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5,  5,  5,  5,  0,-10,
                -5,  0,  5,  5,  5,  5,  0, -5,
                0,  0,  5,  5,  5,  5,  0, -5,
                -10,  5,  5,  5,  5,  5,  0,-10,
                -10,  0,  5,  0,  0,  0,  0,-10,
                -20,-10,-10, -5, -5,-10,-10,-20
            ],
            'King' : [
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -20,-30,-30,-40,-40,-30,-30,-20,
                -10,-20,-20,-20,-20,-20,-20,-10,
                20, 20,  0,  0,  0,  0, 20, 20,
                20, 30, 10,  0,  0, 10, 30, 20
            ]
        }

    def materialEvaluate(self, board: Type[Board]) -> int:
        """
        Calculate the material advantage for a given position by finding the sum
        of the piece values on each team and taking the difference.
        """
        score = 0

        for r in range(8):
            for c in range(8):
                if (square := board.squares[r][c]) is not None:
                    score += square.value if square.team else -square.value

        return score

    def positionEvaluate(self, board: Type[Board]) -> int:
        """
        Calculate the material advantage for a given position by finding the sum
        of the product of piece's value and its corresponding position score for
        each team and taking the difference.
        """
        score = 0

        for r in range(8):
            for c in range(8):
                if (square := board.squares[r][c]) is not None:
                    score += self.position_scores[square.__class__.__name__] \
                        [((r * 8) + c) if square.team else ((7 - r) * 8 + c)] \
                        * (square.value if square.team else -square.value)
        return score
    
    def controlEvaluate(self, board: Type[Board]) -> int:
        """
        Calculate the material advantage for a given position by finding the sum
        of the product of piece's value and the count of squares it is attacking
        for each team and taking the difference.
        """
        # Example: A white knight is attackign 2 squares. Knights have a score of
        # 3, so the space-control score for the knight would be 3 * 2 = 6.
        score = 0

        for r in range(8):
            for c in range(8):
                if (square := board.squares[r][c]) is not None:
                    score += len(board.control_mtx[r][c]) \
                        * (square.value if square.team else -square.value)
        
        return score
    
    def evaluate(self, board: Type[Board]) -> int:
        """
        Given a board, evaluate the position based on the material, position, and
        space-control advanges.
        """
        POSITION_WEIGHT = 0.15
        MATERIAL_WEIGHT = 46
        CONTROL_SCORE = 1
        position_score = POSITION_WEIGHT * self.positionEvaluate(board)
        material_score = MATERIAL_WEIGHT * self.materialEvaluate(board)
        control_score = CONTROL_SCORE * self.controlEvaluate(board)

        return position_score + material_score + control_score