import random

class Bot:
	def __init__(self, depth: int):
		self.depth = depth

	def minimax(self, board: object, team: bool, cur_depth: int) -> int:
		# bad practice to make a model inside of bot, p sure this is the simplest way to do this
		# maybe model has bot and engine fields, uses those to call these functions, can just pass in legal moves to minimax?

		# for every legal move on this board, try every legal move after every legal move -> do this depth times
		# once at leaf, calculate best move and it's score
		# compare that against all others, pass it up
		# repeat until single move chosen
		# incorporate ab later
		pass

