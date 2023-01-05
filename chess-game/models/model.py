from models.board import Board
from models.pieces import Knight, Bishop, Rook, Queen

class Model:
	def __init__(self):
		self.board = Board()
		self.black_king_pos = (0, 4)
		self.white_king_pos = (7, 4)

	def validMove(self, move: str, team: bool) -> bool:
		return (len(move) == 4) and (all([(c.isnumeric() and (int(c) in range(8))) for c in move])) \
			and (move[:2] != move[2:])

	def legalMove(self, move: str):
		move = tuple(int(c) for c in move)  # need to use tuple() b/c (for...) is generator expression
		return move in self.legal_moves

	def movePiece(self, move: str) -> None:
		'''
		precondition: move is legal
		'''

		def promote() -> str:
			inp = None
			while inp not in ("Pawn", "Knight", "Bishop", "Queen"):
				inp = input("promote pawn to ... (\"Pawn\", \"Knight\", \"Bishop\", \"Queen\")\n").strip()
			return inp

		move = tuple(int(c) for c in move)  # need to use tuple() b/c (for...) is generator expression
		if move not in self.legal_moves:
			return
		r, c, r1, c1 = move
		# short castle
		if move in ((0, 4, 0, 6), (7, 4, 7, 6)):
			self.board.squares[r][4].moved, self.board.squares[r][7].moved = True, True  # could do this with a = b = True
			self.board.squares[r][4], self.board.squares[r][6] = None, self.board.squares[r][4]
			self.board.squares[r][7], self.board.squares[r][5] = None, self.board.squares[r][7]
		# long castle
		elif move in ((0, 4, 0, 2), (7, 4, 7, 2)):
			self.board.squares[r][4].moved, self.board.squares[r][0].moved = True, True  # could do this with a = b = True
			self.board.squares[r][4], self.board.squares[r][2] = None, self.board.squares[r][4]
			self.board.squares[r][0], self.board.squares[r][3] = None, self.board.squares[r][0]
		# other moves
		else:
			if (cur := self.board.squares[r][c]).__class__.__name__ in ("Pawn", "Rook", "King"):
				cur.moved = True
			self.board.squares[r1][c1], self.board.squares[r][c] = self.board.squares[r][c], None
			if ((cur := self.board.squares[r1][c1]).__class__.__name__ == "Pawn") and (r1 in (0, 7)):
				match promote():
					case "Pawn":
						pass
					case "Knight":
						self.board.squares[r1][c1] = Knight(cur.team)
					case "Bishop":
						self.board.squares[r1][c1] = Bishop(cur.team)
					case "Rook":
						self.board.squares[r1][c1] = Rook(cur.team)
						self.board.squares.moved = True
					case "Queen":
						self.board.squares[r1][c1] = Queen(cur.team)
		# update king pos
		if (cur := self.board.squares[r1][c1]).__class__.__name__ == "King":
			if cur.team:
				self.white_king_pos = (r1, c1)
			else:
				self.black_king_pos = (r1, c1)

	def checkCheck(self, team: bool) -> bool:
		
		def controls(r: int, c: int, team: bool) -> bool:
			return any([(p[2] == team) for p in self.control_mtx[r][c]])

		return controls(self.white_king_pos[0], self.white_king_pos[1], False) if team \
			else controls(self.black_king_pos[0], self.black_king_pos[1], True)			
	
	def checkMate(self, team: bool) -> bool:
		'''
		precondition: king is under check

		"escape" mate three criteria:
		1) move out of the way
			- there is at least one non-occupied square around the king that is not under opp control
			* if king in double-check (check + discovered check), this is the only option
		2) capture attacking piece
			- cur team can capture piece checking king
			* if king can capture, that piece must not be defended
		3) block check
			- cur team has at least one piece that can block opp attack (except knight)
		'''

		def controls(r: int, c: int, team: bool) -> bool:
			# non-king piece controls this square
			return any([((p[2] == team) and (tuple(p[:2]) != (self.white_king_pos if team else self.black_king_pos))) for p in self.control_mtx[r][c]])
		
		r, c = self.white_king_pos if team else self.black_king_pos
		# case 1: move out of the way
		print("case 1")
		if any([((r, c) == tuple(m[:2])) for m in self.legal_moves]):
			return False
		# edge case 1: double check
		print("edge 1")
		aps = [p for p in self.control_mtx[r][c] if (p[2] != team)]  # attacking pieces
		if len(aps) > 1:
			return True
		# case 2: capture attacking piece
		print("case 2")
		ar, ac = aps[0][:2]  # attacking piece row, col
		# cur team can capture attacking piece (not king, case 1 covers this)
		if any([((p[2] == team) and (p[3] != "King")) for p in self.control_mtx[ar][ac]]):
			return False
		# case 3: block check
		print("case 3")
		match aps[0][3]:
			case "Pawn":
				# can't block pawn
				pass
			case "Knight":
				# can't block knight
				pass
			case "Bishop":
				r1, c1 = r, c
				dr, dc = 1 if (ar > r1) else -1, 1 if (ac > c1) else -1
				r1 += dr
				c1 += dc
				while (r1 != ar) and (c1 != ac):
					if controls(r1, c1, team):
						return False
					r1 += dr
					c1 += dc
			case "Rook":
				# col
				if r == ar:
					dc = 1 if (ac > c) else -1
					c1 = c + dc
					while c1 != ac:
						if controls(r, c1, team):
							return False
						c1 += dc
				# row
				else:
					dr = 1 if (ar > r) else -1
					r1 = r + dr
					while r1 != ar:
						if controls(r1, c, team):
							return False
						r1 += dr
			case "Queen":
				# col
				if r == ar:
					dc = 1 if (ac > c) else -1
					c1 = c + dc
					while c1 != ac:
						if controls(r, c1, team):
							return False
						c1 += dc
				# row
				elif c == ac:
					dr = 1 if (ar > r) else -1
					r1 = r + dr
					while r1 != ar:
						if controls(r1, c, team):
							return False
						r1 += dr
				# diagonal
				else:
					r1, c1 = r, c
					dr, dc = 1 if (ar > r1) else -1, 1 if (ac > c1) else -1
					r1 += dr
					c1 += dc
					while (r1 != ar) and (c1 != ac):
						if controls(r1, c1, team):
							return False
						r1 += dr
						c1 += dc
			case _:
				pass
		# failed all escape conditions, it's mate
		return True

	def checkStale(self, team: bool) -> bool:
		return not self.legal_moves

	def generateControlMatrix(self) -> None:

		def inBounds(x: int) -> bool:
			return x in range(8)

		def addControl(r: int, c: int, r1: int, c1: int, piece_type: str) -> None:
			#? should i even include team and piece type? can just get this from control mtx later
			mtx[r1][c1].append((r, c, team, piece_type))

		mtx = [[[] for _ in range(8)] for _ in range(8)]
		for r in range(8):
			for c in range(8):
				if cur := self.board.squares[r][c]:
					team = cur.team
					match cur.__class__.__name__:
						case "Pawn":
							dr = -1 if team else 1
							if inBounds(sr := r + dr):
								if inBounds(sc := c + 1):
									addControl(r, c, sr, sc, "Pawn")
								if inBounds(sc := c - 1):
									addControl(r, c, sr, sc, "Pawn")
						case "Knight":
							moves = ((2, 1), (2, -1), (-2, 1), (-2, -1), \
									 (1, 2), (1, -2), (-1, 2), (-1, -2))
							for m in moves:
								if inBounds(sr := r + m[0]) and inBounds(sc := c + m[1]):
									addControl(r, c, sr, sc, "Knight")
						case "Bishop":
							dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))
							for d in dirs:
								r1, c1 = r + d[0], c + d[1]
								while inBounds(r1) and inBounds(c1):
									addControl(r, c, r1, c1, "Bishop")
									if self.board.squares[r1][c1]:
										break
									r1 += d[0]
									c1 += d[1]
						case "Rook":
							deltas = (1, -1)
							for d in deltas:
								r1, c1 = r + d, c + d
								while inBounds(r1):
									addControl(r, c, r1, c, "Rook")
									if self.board.squares[r1][c]:
										break
									r1 += d
								while inBounds(c1):
									addControl(r, c, r, c1, "Rook")
									if self.board.squares[r][c1]:
										break
									c1 += d
						case "Queen":
							# diagonal
							dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))
							for d in dirs:
								r1, c1 = r + d[0], c + d[1]
								while inBounds(r1) and inBounds(c1):
									addControl(r, c, r1, c1, "Queen")
									if self.board.squares[r1][c1]:
										break
									r1 += d[0]
									c1 += d[1]
							# straight
							deltas = (1, -1)
							for d in deltas:
								r1, c1 = r + d, c + d
								while inBounds(r1):
									addControl(r, c, r1, c, "Queen")
									if self.board.squares[r1][c]:
										break
									r1 += d
								while inBounds(c1):
									addControl(r, c, r, c1, "Queen")
									if self.board.squares[r][c1]:
										break
									c1 += d
						case "King":
							moves = ((1, 1), (1, 0), (1, -1), (0, -1), \
									 (-1, -1), (-1, 0), (-1, 1), (0, 1))
							for m in moves:
								if inBounds(sr := r + m[0]) and inBounds(sc := c + m[1]):
									addControl(r, c, sr, sc, "King")
						case _:
							pass
		self.control_mtx = mtx

	def generatePositionMatrix(self) -> None:
		mtx = [[None for _ in range(8)] for _ in range(8)]
		for r in range(8):
			for c in range(8):
				cur = self.board.squares[r][c]
				mtx[r][c] = cur.team if cur else None
		self.position_mtx = mtx

	def generateLegalMoves(self, team: bool) -> None:

		def inBounds(x: int) -> bool:
			return x in range(8)

		def addMove(r: int, c: int, r1: int, c1: int) -> None:
			legal.append((r, c, r1, c1))

		legal = []
		for r in range(8):
			for c in range(8):
				if cur := self.board.squares[r][c]:
					team = cur.team
					match cur.__class__.__name__:
						case "Pawn":
							dr = -1 if team else 1
							if inBounds(sr := r + dr):
								if self.position_mtx[sr][c] == None:
									addMove(r, c, sr, c)
								if inBounds(sc := c + 1) and (self.position_mtx[sr][sc] not in (None, team)):
									addMove(r, c, sr, sc)
								if inBounds(sc := c - 1) and (self.position_mtx[sr][sc] not in (None, team)):
									addMove(r, c, sr, sc)
							if inBounds(dr2 := sr + dr) and (not cur.moved) and (self.position_mtx[sr][c] == self.position_mtx[dr2][c] == None):
								addMove(r, c, dr2, c)
						case "Knight":
							moves = ((2, 1), (2, -1), (-2, 1), (-2, -1), \
									 (1, 2), (1, -2), (-1, 2), (-1, -2))
							for m in moves:
								if inBounds(sr := r + m[0]) and inBounds(sc := c + m[1]) and (self.position_mtx[sr][sc] != team):
									addMove(r, c, sr, sc)
						case "Bishop":
							dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))
							for d in dirs:
								r1, c1 = r + d[0], c + d[1]
								while inBounds(r1) and inBounds(c1) and (self.position_mtx[r1][c1] != team):
									addMove(r, c, r1, c1)
									if self.position_mtx[r1][c1] != None:
										break
									r1 += d[0]
									c1 += d[1]
						case "Rook":
							deltas = (1, -1)
							for d in deltas:
								r1, c1 = r + d, c + d
								while inBounds(r1) and (self.position_mtx[r1][c] != team):
									addMove(r, c, r1, c)
									if self.position_mtx[r1][c] != None:
										break
									r1 += d
								while inBounds(c1) and (self.position_mtx[r][c1] != team):
									addMove(r, c, r, c1)
									if self.position_mtx[r][c1] != None:
										break
									c1 += d
						case "Queen":
							# diagonal
							dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))
							for d in dirs:
								r1, c1 = r + d[0], c + d[1]
								while inBounds(r1) and inBounds(c1) and (self.position_mtx[r1][c1] != team):
									addMove(r, c, r1, c1)
									if self.position_mtx[r1][c1] != None:
										break
									r1 += d[0]
									c1 += d[1]
							# straight
							deltas = (1, -1)
							for d in deltas:
								r1, c1 = r + d, c + d
								while inBounds(r1) and (self.position_mtx[r1][c] != team):
									addMove(r, c, r1, c)
									if self.position_mtx[r1][c] != None:
										break
									r1 += d
								while inBounds(c1) and (self.position_mtx[r][c1] != team):
									addMove(r, c, r, c1)
									if self.position_mtx[r][c1] != None:
										break
									c1 += d
						case "King":
							moves = ((1, 1), (1, 0), (1, -1), (0, -1), \
									 (-1, -1), (-1, 0), (-1, 1), (0, 1))
							for m in moves:
								if inBounds(sr := r + m[0]) and inBounds(sc := c + m[1]) \
									and (self.position_mtx[sr][sc] != team) \
									and (not any([(p[2] != team) for p in self.control_mtx[sr][sc]])):
									addMove(r, c, sr, sc)
							# castle
							if (not cur.moved):
								# short
								if ((rook := self.board.squares[r][7]) != None) and (rook.__class__.__name__ == "Rook") and (not rook.moved) \
									and (self.board.squares[r][5] == self.board.squares[r][6] == None):
									addMove(r, 4, r, 6)
								# long
								if ((rook := self.board.squares[r][0]) != None) and (rook.__class__.__name__ == "Rook") and (not rook.moved) \
									and (self.board.squares[r][1] == self.board.squares[r][2] == self.board.squares[r][3] == None):
									addMove(r, 4, r, 2)
						case _:
							pass
		self.legal_moves = legal

	def printBoard(self) -> None:
		print("    0  1  2  3  4  5  6  7")
		print("  +------------------------+")
		for r in range(8):
			print(f"{r} |", end="")
			for c in range(8):
				cur = self.board.squares[r][c]
				if cur:
					match cur.__class__.__name__:
						case "Pawn":
							print(" P " if cur.team else " p ", end="")
						case "Knight":
							print(" N " if cur.team else " n ", end="")
						case "Bishop":
							print(" B " if cur.team else " b ", end="")
						case "Rook":
							print(" R " if cur.team else " r ", end="")
						case "Queen":
							print(" Q " if cur.team else " q ", end="")
						case "King":
							print(" K " if cur.team else " k ", end="")
						case _:
							pass
				else:
					print(" ∙ ", end="") # ∙□.-
			print("|")
		print("  +------------------------+")

	def printControlMatrix(self) -> None:
		for r in range(8):
			print(f"ROW {r} =>    ", end = "")
			for c in range(8):
				print(self.control_mtx[r][c], end = "    ")
			print()

	def printPositionMatrix(self) -> None:
		for r in range(8):
			print(f"ROW {r} =>    ", end = "")
			for c in range(8):
				print(self.position_mtx[r][c], end = "  ")
			print()
