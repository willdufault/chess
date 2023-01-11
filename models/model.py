from models.engine import Engine
from models.bot import Bot
from models.board import Board
from models.pieces import Knight, Bishop, Rook, Queen

class Model:
	def __init__(self, depth: int):
		self.board = Board()
		self.engine = Engine()
		self.bot = Bot(depth, self.engine)
		self.move_cnt = 0

	def validMove(self, move: tuple[int]) -> bool:
		'''
		if move follows correct format: len 4, all ints, second half != first half
		'''
		return (len(move) == 4) and all([(x < 9) for x in move]) and (move[:2] != move[2:])
	
	def legalMove(self, move: tuple[int]) -> bool:
		'''
		precondition: move is valid

		if move is a legal move on the board
		'''
		r, c, rx, cx = move
		return (r, c, rx, cx) in self.board.legal_moves
	
	def updateMoveCount(self) -> None:
		self.move_cnt += 1