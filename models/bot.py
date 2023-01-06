import math
import random
from models.engine import Engine

class Bot:
	def __init__(self, depth: int):
		self.depth = depth
		# could pass bot an engine to use from model

	def bot_move(self, board: object, team: bool) -> None:
		moves = board.legal_moves  # all legal moves for this board and team
		scores = []  # scores for each move
		for i, m in enumerate(moves):
			r, c, r1, c1 = m
			old, old1 = board.squares[r][c], board.squares[r1][c1]
			board.movePiece(str(r) + str(c) + str(r1) + str(c1))

			scores.append((self.minimax_ab(team, self.depth - 1, -math.inf, math.inf, board), i))
			# undo move
			board.squares[r][c], board.squares[r1][c1] = old, old1
		best_score = max(scores) if team else min(scores)
		# random choice of this, fix syntax
		choices = [s for s in scores if (s == (max(scores) if team else min(scores)))]  # moves that have best score
		best_move = moves[random.choice(choices)[1]]  # best_move
		board.movePiece(str(best_move[0]) + str(best_move[1]) + str(best_move[2]) + str(best_move[3]))

	def minimax(self, team: bool, depth: int, board: object) -> int:
		'''
		for every legal move, try it and its legal moves (depth times), find the move with the greatest outcome
		'''
		board.generateControlMatrix()
		board.generatePositionMatrix()
		board.generateLegalMoves(team)
		# stalemate
		if board.checkStale(team):
			return 0
		# checkmate
		if board.checkMate(team):
			#? add tuple (cur_depth, score) so M1 is picked over M3?
			#* mate score arbitrary for now
			return -20 if team else 20
		# reached desired depth
		if not depth:
			return Engine.simpleEvaluate(Engine, board)
		moves = board.legal_moves  # all legal moves for this board
		scores = []  # scores for all legal moves
		for m in moves:
			r, c, r1, c1 = m
			old, old1 = board.squares[r][c], board.squares[r1][c1]
			board.movePiece(str(r) + str(c) + str(r1) + str(c1))
			scores.append(self.minimax(not team, depth - 1, board))
			# undo move
			board.squares[r][c], board.squares[r1][c1] = old, old1
		return max(scores) if team else min(scores)

	def minimax_ab(self, team: bool, depth: int, a: int, b: int, board: object) -> int:
		'''
		for every legal move, try it and its legal moves (depth times), find the move with the greatest outcome
		* with alpha-beta pruning to eliminate unnecessary calls
		* to start, a (high) = -oo, b (low) = oo
		'''
		board.generateControlMatrix()
		board.generatePositionMatrix()
		board.generateLegalMoves(team)
		# stalemate
		if board.checkStale(team):
			return 0
		# checkmate
		if board.checkMate(team):
			#? add tuple (cur_depth, score) so M1 is picked over M3?
			#? or add higher score if depth is higher/earlier?)
			#* mate score arbitrary for now
			return -20 if team else 20
		# reached desired depth
		if not depth:
			return Engine.simpleEvaluate(Engine, board)
		moves = board.legal_moves  # all legal moves for this board
		scores = []  # scores for all legal moves
		for m in moves:
			r, c, r1, c1 = m
			old, old1 = board.squares[r][c], board.squares[r1][c1]
			board.movePiece(str(r) + str(c) + str(r1) + str(c1))
			scores.append(score := self.minimax_ab(not team, depth - 1, a, b, board))
			# undo move
			board.squares[r][c], board.squares[r1][c1] = old, old1
			# maximizing
			if team:
				a = max(a, score)
			# minimizing
			else:
				b = min(b, score)
			if a > b:
				break
		return max(scores) if team else min(scores)