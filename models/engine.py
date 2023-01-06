class Engine:
	def __init__(self):
		pass
		# have 8x8 board in self to get points for that piece
		# ex: self.center = 8x8 board with higher points in the center, use that to eval pieces on those squares

	def simpleEvaluate(self, board: object) -> int:
		# just sum up all piece values for both teams
		score = 0
		for r in range(8):
			for c in range(8):
				if cur := board.squares[r][c]:
					score += cur.value if cur.team else -cur.value
		return score