class Bot:
	def __init__(self, board: object, depth: int):
		self.board = board
		self.depth = depth

	def minimax(self):
		# for every legal move on this board, try every legal move after every legal move -> do this depth times
		# once at leaf, calculate best move and it's score
		# compare that against all others, pass it up
		# repeat until single move chosen
		# incorporate ab later
		pass

