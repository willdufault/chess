from models.engine import Engine
import math
import random

class Bot:
	def __init__(self, depth: int, engine: object):
		self.depth = depth
		self.engine = engine
		self.memo = {}  # board memoization
		# could pass bot an engine to use from model
		# add memoization somehow so if we see position we've already seen, we can just save it

	def bot_move(self, board: object, team: bool) -> None:
		# re-generate matrices
		board.generateControlMatrix()
		board.generatePositionMatrix()
		board.generateLegalMoves(team)
		moves = board.legal_moves  # all legal moves for this board and team
		scores = []  # scores for each move
		for i, m in enumerate(moves):
			r, c, r1, c1 = m  # cur move
			move_tup = (r, c, r1, c1, board.squares[r][c], board.squares[r1][c1], \
				board.squares[r][c].moved if hasattr(board.squares[r][c], "moved") else None)  # tuple of directions for this move
			board.botMovePiece(m)
			# add move score
			scores.append((self.minimax_ab_memo(team, self.depth, -math.inf, math.inf, board), i))
			board.undoMove(move_tup)
			# re-generate matrices
			board.generateControlMatrix()
			board.generatePositionMatrix()
			board.generateLegalMoves(team)
		# random choice of this, fix syntax
		choices = [s for s in scores if (s[0] == (max(scores, key = lambda s:s[0])[0] if team else min(scores, key = lambda s:s[0])[0]))]
		print("scores:", scores, "\nchoices:", choices)
		best_move = moves[(random.choice(choices)[1])]  # best_move
		# make move
		board.botMovePiece(best_move)

	def minimax_ab_memo(self, team: bool, depth: int, a: int, b: int, board: object) -> int:
		'''
		for every legal move, try it and its legal moves (depth times), find the move with the greatest outcome
		* with alpha-beta pruning to eliminate unnecessary calls (to start, a (high) = -oo, b (low) = oo)
		* also added memoization
		'''

		def hashBoard(board: int) -> tuple[int]:
			key = []
			for r in range(8):
				for c in range(8):
					key.append(board.squares[r][c])
			return tuple(key)
		
		# re-generate matrices
		board.generateControlMatrix()
		board.generatePositionMatrix()
		board.generateLegalMoves(team)
		# stalemate
		if board.checkStale(team):
			return 0
		# checkmate
		if board.checkMate(team):
			#* mate score arbitrary for now
			return (-200  if team else 200) * depth
		# reached desired depth
		if not depth:
			return self.engine.evaluate(board)
		moves = board.legal_moves
		scores = []  # scores for all legal moves
		for m in moves:
			# print("inner: ", moves)
			score = 0  # score for this pos
			r, c, r1, c1 = m  # cur move
			move_tup = (r, c, r1, c1, board.squares[r][c], board.squares[r1][c1], \
				board.squares[r][c].moved if hasattr(board.squares[r][c], "moved") else None)  # tuple of directions for this move
			# bot makes move
			board.botMovePiece(m)
			key = hashBoard(board)  # key for this board config
			# already seen this
			if key in self.memo:
				scores.append(score := self.memo[key])
				# print(":) memo")
			# new board
			else:
				scores.append(score := self.minimax_ab_memo(not team, depth - 1, a, b, board))
				# add to memo
				self.memo[key] = score
			# undo move
			board.undoMove(move_tup)
			# re-generate matrices
			board.generateControlMatrix()
			board.generatePositionMatrix()
			board.generateLegalMoves(team)
			# maximizing
			if team:
				a = max(a, score)
			# minimizing
			else:
				b = min(b, score)
			if a > b:
				break
		return max(scores) if team else min(scores)

	'''
	def minimax_ab(self, team: bool, depth: int, a: int, b: int, board: object) -> int:
		# stalemate
		if board.checkStale(team):
			return 0
		# checkmate
		if board.checkMate(team):
			#? add tuple (cur_depth, score) so M1 is picked over M3? or add higher score if depth is higher/earlier?
			#* mate score arbitrary for now
			return -20 if team else 20
		# reached desired depth
		if not depth:
			return Engine.simpleEvaluate(Engine, board)
		# re-generate matrices
		board.generateControlMatrix()
		board.generatePositionMatrix()
		board.generateLegalMoves(team)
		moves = board.legal_moves
		scores = []  # scores for all legal moves
		for m in moves:
			# print("inner: ", moves)
			score = 0  # score for this pos
			r, c, r1, c1 = m  # cur move
			move_tup = (r, c, r1, c1, board.squares[r][c], board.squares[r1][c1], \
				board.squares[r][c].moved if hasattr(board.squares[r][c], "moved") else None)  # tuple of directions for this move
			# bot makes move
			board.botMovePiece(m)
			scores.append(score := self.minimax_ab(not team, depth - 1, a, b, board))
			# undo move
			board.undoMove(move_tup)
			# re-generate matrices
			board.generateControlMatrix()
			board.generatePositionMatrix()
			board.generateLegalMoves(team)
			# maximizing
			if team:
				a = max(a, score)
			# minimizing
			else:
				b = min(b, score)
			if a > b:
				break
		return max(scores) if team else min(scores)
	'''

	'''
	def minimax(self, team: bool, depth: int, board: object) -> int:
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
	'''