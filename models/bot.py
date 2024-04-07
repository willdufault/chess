import math
import random

class Bot:
	def __init__(self, depth: int, engine: object):
		self.depth = depth
		self.engine = engine
		self.memo = {}  # board memoization

	def bestMove(self, board: object, team: bool, move_count: int) -> tuple[int]:
		'''
		precondition: legal moves updated for cur pos
		'''
		scores = []  # scores for each move
		moves = board.legal_moves  # all legal moves for this board and team
		# sort nodes with potential good moves first to maximize potential for pruning
		# in detail: sort first by pieces with a low positional score, then sort by piece value, reverse for highest potential strength moves first
		moves.sort(key=lambda m:self.engine.position_scores[board.squares[m[0]][m[1]].__class__.__name__][((m[0] * 8) + m[1]) if board.squares[m[0]][m[1]].team else ((7 - m[0]) * 8 + m[1])] \
			* -board.squares[m[0]][m[1]].value, reverse=True)
		for m in moves:
			r, c, rx, cx = m  # cur move
			p1, p2 = board.squares[r][c], board.squares[rx][cx]
			p1_moved = p1.moved if hasattr(p1, "moved") else None
			board.botMove(r, c, rx, cx)
			# add move score
			scores.append((self.minimax_ab_memo(team, self.depth, move_count + 1, -math.inf, math.inf, board), r, c, rx, cx))
			board.undo(r, c, rx, cx, p1, p2, p1_moved)
			board.revertControlMatrix(r, c, rx, cx, p1, p2)
			board.generatePositionMatrix()
		# random choice of all moves with the highest/lowest score
		choices = [s for s in scores if (s[0] == (max(scores, key = lambda s:s[0])[0] if team else min(scores, key = lambda s:s[0])[0]))]
		_, best_r, best_c, best_rx, best_cx = random.choice(choices)
		board.botMove(best_r, best_c, best_rx, best_cx)
		return (best_r, best_c, best_rx, best_cx)

	def minimax_ab_memo(self, team: bool, depth: int, move_count: int, a: int, b: int, board: object) -> int:
		'''
		for every legal move, try it and its legal moves (depth times), find the move with the greatest outcome
		* with alpha-beta pruning to eliminate unnecessary calls (to start, a (high) = -oo, b (low) = oo)
		* also added memoization
		'''

		def hashBoard(board: int) -> tuple[int]:
			'''
			given a board config, return a tuple with all the board's info
			'''
			key = []
			for r in range(8):
				for c in range(8):
					key.append(board.squares[r][c])
			return tuple(key)
	
		board.generateLegalMoves(team)
		if board.stalemate(team, move_count):
			return 0
		if board.checkmate(team):
			return (-300 if team else 300) * depth
		# reached desired depth
		if not depth:
			# return board evaluation for cur board
			return self.engine.evaluate(board)
		moves = board.legal_moves
		scores = []  # scores for all legal moves
		for m in moves:
			score = 0  # score for this pos
			r, c, rx, cx = m  # cur move
			p1, p2 = board.squares[r][c], board.squares[rx][cx]
			p1_moved = p1.moved if hasattr(p1, "moved") else None
			board.botMove(r, c, rx, cx)
			key = hashBoard(board)  # key for this board config
			# already seen this
			if key in self.memo:
				scores.append(score := self.memo[key])
			# new board
			else:
				scores.append(score := self.minimax_ab_memo(not team, depth - 1, move_count + 1, a, b, board))
				# add to memo
				self.memo[key] = score
			# undo move, revert game state
			board.undo(r, c, rx, cx, p1, p2, p1_moved)
			board.revertControlMatrix(r, c, rx, cx, p1, p2)
			board.generatePositionMatrix()
			# maximizing
			if team:
				a = max(a, score)
			# minimizing
			else:
				b = min(b, score)
			if a > b:
				break
		return max(scores) if team else min(scores)
