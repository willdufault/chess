class Pawn:
	def __init__(self, team: bool):
		self.team = team
		self.value = 1
		self.moved = False  # for moving up two

class Knight:
	def __init__(self, team: bool):
		self.team = team
		self.value = 3

class Bishop:
	def __init__(self, team: bool):
		self.team = team
		self.value = 3

class Rook:
	def __init__(self, team: bool):
		self.team = team
		self.value = 5
		self.moved = False  # for castling

class Queen:
	def __init__(self, team: bool):
		self.team = team
		self.value = 9

class King:
	def __init__(self, team: bool):
		self.team = team
		self.value = 99  # priceless
		self.moved = False  # for castling
