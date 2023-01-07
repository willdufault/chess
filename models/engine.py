class Engine:
	def __init__(self):
		self.positionScores = {
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
				"Knight" : [
					-50,-40,-30,-30,-30,-30,-40,-50,
					-40,-20,  0,  0,  0,  0,-20,-40,
					-30,  0, 10, 15, 15, 10,  0,-30,
					-30,  5, 15, 20, 20, 15,  5,-30,
					-30,  0, 15, 20, 20, 15,  0,-30,
					-30,  5, 10, 15, 15, 10,  5,-30,
					-40,-20,  0,  5,  5,  0,-20,-40,
					-50,-40,-30,-30,-30,-30,-40,-50
				],
				"Bishop" : [
					-20,-10,-10,-10,-10,-10,-10,-20,
					-10,  0,  0,  0,  0,  0,  0,-10,
					-10,  0,  5, 10, 10,  5,  0,-10,
					-10,  5,  5, 10, 10,  5,  5,-10,
					-10,  0, 10, 10, 10, 10,  0,-10,
					-10, 10, 10, 10, 10, 10, 10,-10,
					-10,  5,  0,  0,  0,  0,  5,-10,
					-20,-10,-10,-10,-10,-10,-10,-20
				],
				"Rook" : [
					0,  0,  0,  0,  0,  0,  0,  0,
					5, 10, 10, 10, 10, 10, 10,  5,
					-5,  0,  0,  0,  0,  0,  0, -5,
					-5,  0,  0,  0,  0,  0,  0, -5,
					-5,  0,  0,  0,  0,  0,  0, -5,
					-5,  0,  0,  0,  0,  0,  0, -5,
					-5,  0,  0,  0,  0,  0,  0, -5,
					0,  0,  0,  5,  5,  0,  0,  0
				],
				"Queen" : [
					-20,-10,-10, -5, -5,-10,-10,-20,
					-10,  0,  0,  0,  0,  0,  0,-10,
					-10,  0,  5,  5,  5,  5,  0,-10,
					-5,  0,  5,  5,  5,  5,  0, -5,
					0,  0,  5,  5,  5,  5,  0, -5,
					-10,  5,  5,  5,  5,  5,  0,-10,
					-10,  0,  5,  0,  0,  0,  0,-10,
					-20,-10,-10, -5, -5,-10,-10,-20
				],
				"King" : [
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

	def materialEvaluate(self, board: object) -> int:
		# just sum up all piece values for both teams
		score = 0
		for r in range(8):
			for c in range(8):
				if cur := board.squares[r][c]:
					score += cur.value if cur.team else -cur.value
		return score

	def positionEvaluate(self, board: object) -> int:
		score = 0
		for r in range(8):
			for c in range(8):
				if cur := board.squares[r][c]:
					score += self.positionScores[cur.__class__.__name__][((r * 8) + c) if cur.team else ((7 - r) * 8 + c)] * (cur.value if cur.team else -cur.value)
		return score
	
	def evaluate(self, board: object) -> int:
		# todo: optimize/combine this cleanly so that it doesn't run through entire board on every eval
		return 0.1 * self.positionEvaluate(board) + 3 * self.materialEvaluate(board)