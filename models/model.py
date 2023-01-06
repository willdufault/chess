from models.engine import Engine
from models.bot import Bot
from models.board import Board
from models.pieces import Knight, Bishop, Rook, Queen

class Model:
	def __init__(self, depth: int):
		self.board = Board()
		self.engine = Engine()
		self.bot = Bot(depth)
		
	
	