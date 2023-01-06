from models.pieces import Pawn, Knight, Bishop, Rook, Queen, King

class Board:
	def __init__(self):
		self.squares = [[None for _ in range(8)] for _ in range(8)]
		self.initBoard()
	
	def initBoard(self) -> None:
		# pawns
		for c in range(8):
			# black
			self.squares[1][c] = Pawn(False)
			# white
			self.squares[6][c] = Pawn(True)
		# pieces (black, white)
		self.squares[0][0], self.squares[7][0] = Rook(False), Rook(True)
		self.squares[0][1], self.squares[7][1] = Knight(False), Knight(True)
		self.squares[0][2], self.squares[7][2] = Bishop(False), Bishop(True)
		self.squares[0][3], self.squares[7][3] = Queen(False), Queen(True)
		self.squares[0][4], self.squares[7][4] = King(False), King(True)
		self.squares[0][5], self.squares[7][5] = Bishop(False), Bishop(True)
		self.squares[0][6], self.squares[7][6] = Knight(False), Knight(True)
		self.squares[0][7], self.squares[7][7] = Rook(False), Rook(True)