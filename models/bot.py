from .engine import Engine
from .board import Board
import math
import random
from typing import Type, Tuple

class Bot:
    def __init__(self, depth: int, engine: Type[Engine]):
        self.depth = depth
        self.engine = engine
        self.cache = {} # Board memoization.

    def calculateBestMove(self, board: Type[Board], team: bool, move_count: int) -> tuple[int]:
        """
        Calculate the best move (according to the engine) given a board.
        """
        scores = []
        moves = board.legal_moves

        # Sort the moves so that good moves appear first to maximize the potential
        # for pruning.
        # In detail: sort first by pieces with a low position score and second 
        # by pieces with a high value in descending order.
        moves.sort(key=lambda m:self.engine.position_scores[board.squares[m[0]][m[1]].__class__.__name__] \
                   [((m[0] * 8) + m[1]) if board.squares[m[0]][m[1]].team else ((7 - m[0]) * 8 + m[1])] \
                    * -board.squares[m[0]][m[1]].value, reverse=True)
        
        for r, c, rx, cx in moves:
            piece1, piece2 = board.squares[r][c], board.squares[rx][cx]
            piece1_moved = piece1.moved if hasattr(piece1, "moved") else None

            # Test a move.
            board.makeBotMove(r, c, rx, cx)
            scores.append((self.minimax(team, self.depth, move_count + 1, 
                                                -math.inf, math.inf, board), r, c, rx, cx))            
            board.undo(r, c, rx, cx, piece1, piece2, piece1_moved)

            # Revert the control matrix since it was modified in the minimax call.
            board.revertControlMatrix(r, c, rx, cx, piece1, piece2)
            board.generatePositionMatrix()

        # Get the move candidates by checking if they match the best score found.
        candidates = [s for s in scores if (s[0] == (max(scores, key=lambda s:s[0])[0] \
                                                     if team else min(scores, key = lambda s:s[0])[0]))]
        _, best_r, best_c, best_rx, best_cx = random.choice(candidates)

        board.makeBotMove(best_r, best_c, best_rx, best_cx)

        return best_r, best_c, best_rx, best_cx

    def minimax(self, team: bool, depth: int, move_count: int, a: int, b: int, board: Type[Board]) -> int:
        """
        For every legal move, try it and its legal moves up to a given depth to 
        find the move with the best outcome depending on the team.
        * With memoization to eliminate repeat calls.
        * With alpha-beta pruning to prune parts of the game tree (to start, 
          a (high) = -oo, b (low) = oo).
        """

        def hashBoard(board: int) -> Tuple[int]:
            """
            given a board config, return a tuple with all the board's information.
            """
            key = []
            for r in range(8):
                for c in range(8):
                    key.append(board.squares[r][c])
            return tuple(key)
    
        board.generateLegalMoves(team)

        if board.stalemate(team, move_count): return 0
        if board.checkmate(team): return (-300 if team else 300) * depth
        if depth == 0: return self.engine.evaluate(board)

        moves = board.legal_moves
        scores = []

        for r, c, rx, cx in moves:
            score = 0
            piece1, piece2 = board.squares[r][c], board.squares[rx][cx]
            piece1_moved = piece1.moved if hasattr(piece1, 'moved') else None

            # Test a move and store the output.
            board.makeBotMove(r, c, rx, cx)
            key = hashBoard(board)

            if key in self.cache:
                scores.append(score := self.cache[key])
            
            else:
                scores.append(score := self.minimax(not team, depth - 1, move_count + 1, a, b, board))
                self.cache[key] = score

            # Undo the move and revert the game state.
            board.undo(r, c, rx, cx, piece1, piece2, piece1_moved)
            board.revertControlMatrix(r, c, rx, cx, piece1, piece2)
            board.generatePositionMatrix()
            
            # Maximizing.
            if team:
                a = max(a, score)
            
            # Minimizing
            else:
                b = min(b, score)

            # This branch will never be chosen.
            if a > b: break

        return max(scores) if team else min(scores)