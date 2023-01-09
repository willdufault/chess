from models.pieces import Pawn, Knight, Bishop, Rook, Queen, King

class Board:
	def __init__(self):
		self.initBoard()
		self.move_cnt = 0  # move count, 100 per side => auto stalemate
		#todo: update CM and LM definitions with new format
		# control matrix: matrix with tuples (r, c, team, type) where each square has a list of all the pieces that are attacking it on both teams
		# legal moves: list of tuples (r, c, r1, c1) of all legal moves for cur team with cur board 
	
	def initBoard(self) -> None:
		# init squares
		self.squares = [[None for _ in range(8)] for _ in range(8)]
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
		# store king positions
		self.black_king_pos, self.white_king_pos = (0, 4), (7, 4)
	
	def validMove(self, move: str) -> bool:
		'''
		move has to follow the correct format
		'''
		return (len(move) == 4) and (all([(c.isnumeric() and (int(c) in range(8))) for c in move])) \
			and (move[:2] != move[2:])

	# todo
	def legalMove(self, move: str) -> bool:
		'''
		check if move is in list of legal moves
		'''
		move = tuple(int(c) for c in move)  # need to use tuple() b/c (for...) is generator expression
		return move in self.legal_moves

	# todo: need to add updateControlMtx? call before the move? what's the point of that
	def movePiece(self, move: str) -> None:
		'''
		precondition: move is legal
		'''

		def promote() -> str:
			# promote pawn if on last rank
			inp = None
			while inp not in ("Pawn", "Knight", "Bishop", "Queen"):
				inp = input("promote pawn to ... (\"Pawn\", \"Knight\", \"Bishop\", \"Queen\")\n").strip()
			return inp

		move = tuple(int(c) for c in move)  # need to use tuple() b/c (for...) is generator expression
		if move not in self.legal_moves:
			return
		r, c, r1, c1 = move  # r,c = cur pos, r1,c1 = new pos
		# short castle
		if move in ((0, 4, 0, 6), (7, 4, 7, 6)):
			# set both king and rook moved to true
			self.squares[r][4].moved, self.squares[r][7].moved = True, True  # could do this with a = b = True
			# move king + rook
			self.squares[r][4], self.squares[r][6] = None, self.squares[r][4]
			self.squares[r][7], self.squares[r][5] = None, self.squares[r][7]
		# long castle
		elif move in ((0, 4, 0, 2), (7, 4, 7, 2)):
			# set both king and rook moved to true
			self.squares[r][4].moved, self.squares[r][0].moved = True, True  # could do this with a = b = True
			# move king + rook
			self.squares[r][4], self.squares[r][2] = None, self.squares[r][4]
			self.squares[r][0], self.squares[r][3] = None, self.squares[r][0]
		# other moves
		else:
			# if moving pawn, rook, or king, set moved to true
			if hasattr((cur := self.squares[r][c]), "moved"):
				cur.moved = True
			# move piece
			self.squares[r1][c1], self.squares[r][c] = self.squares[r][c], None
			# if pawn and on last rank, promote
			if ((cur := self.squares[r1][c1]).__class__.__name__ == "Pawn") and (r1 in (0, 7)):
				match promote():
					case "Pawn":
						pass
					case "Knight":
						self.squares[r1][c1] = Knight(cur.team)
					case "Bishop":
						self.squares[r1][c1] = Bishop(cur.team)
					case "Rook":
						self.squares[r1][c1] = Rook(cur.team)
						self.squares.moved = True
					case "Queen":
						self.squares[r1][c1] = Queen(cur.team)
		# if moving king, update king pos
		if (cur := self.squares[r1][c1]).__class__.__name__ == "King":
			if cur.team:
				self.white_king_pos = (r1, c1)
			else:
				self.black_king_pos = (r1, c1)
		# update move count
		self.cnt += 1

	# todo: same as movePiece()
	def botMovePiece(self, move: str) -> None:
		'''
		same as move piece but auto-promotion to queen
		'''
		if move not in self.legal_moves:
			print(move, " not in legal moves")		
			return
		r, c, r1, c1 = move  # r,c = cur pos, r1,c1 = new pos
		# short castle
		if move in ((0, 4, 0, 6), (7, 4, 7, 6)):
			# set both king and rook moved to true
			self.squares[r][4].moved, self.squares[r][7].moved = True, True  # could do this with a = b = True
			# move king + rook
			self.squares[r][4], self.squares[r][6] = None, self.squares[r][4]
			self.squares[r][7], self.squares[r][5] = None, self.squares[r][7]
		# long castle
		elif move in ((0, 4, 0, 2), (7, 4, 7, 2)):
			# set both king and rook moved to true
			self.squares[r][4].moved, self.squares[r][0].moved = True, True  # could do this with a = b = True
			# move king + rook
			self.squares[r][4], self.squares[r][2] = None, self.squares[r][4]
			self.squares[r][0], self.squares[r][3] = None, self.squares[r][0]
		# other moves
		else:
			# if moving pawn, rook, or king, set moved to true
			if hasattr((cur := self.squares[r][c]), "moved"):
				cur.moved = True
			# move piece
			self.squares[r1][c1], self.squares[r][c] = self.squares[r][c], None
			# if pawn and on last rank, promote
			if ((cur := self.squares[r1][c1]).__class__.__name__ == "Pawn") and (r1 in (0, 7)):
				self.squares[r1][c1] = Queen(cur.team)
		# if moving king, update king pos
		if (cur := self.squares[r1][c1]).__class__.__name__ == "King":
			if cur.team:
				self.white_king_pos = (r1, c1)
			else:
				self.black_king_pos = (r1, c1)
		# update move count
		self.cnt += 1

	# todo: update control mtx and legal move (make function that does both given r,c,r1,c1 ?)
	def undoMove(self, move: tuple[int, object, bool]) -> None:
		'''
		undo given move
		'''
		r, c, r1, c1, old, old1, moved = move
		# short castle
		if (old.__class__.__name__ == "King") and ((r, c, r1, c1) in ((0, 4, 0, 6), (7, 4, 7, 6))):
			self.squares[r][4], self.squares[r][7] = self.squares[r][6], self.squares[r][5]
			self.squares[r][5], self.squares[r][6] = None, None # can do a = b = None
			self.squares[r][4].moved = False
			self.squares[r][7].moved = False
		# long castle
		elif (old.__class__.__name__ == "King") and ((r, c, r1, c1) in ((0, 4, 0, 2), (7, 4, 7, 2))):
			self.squares[r][4], self.squares[r][0] = self.squares[r][2], self.squares[r][3]
			self.squares[r][1], self.squares[r][2], self.squares[r][3] = None, None, None # can do a = b = c = None
			self.squares[r][4].moved = False
			self.squares[r][0].moved = False
		# other move
		else:
			self.squares[r][c], self.squares[r1][c1] = old, old1
			if hasattr(self.squares[r][c], "moved"):
				self.squares[r][c].moved = moved

	# todo: redo with new PM
	def check(self, team: bool) -> bool:
		
		def controls(r: int, c: int, team: bool) -> bool:
			# does cur team control r,c
			return any([(p[2] == team) for p in self.control_mtx[r][c]])

		return controls(self.white_king_pos[0], self.white_king_pos[1], False) if team \
			else controls(self.black_king_pos[0], self.black_king_pos[1], True)			
	
	# todo: need a way to check for empty matrix since legal moves is no longer a a list
	def checkMate(self, team: bool) -> bool:

		def noLegalMoves(self) -> bool:
			for r in range(8):
				for c in range(8):
					if self.legal_moves[r][c]:
						return False
			return True

		# no legal moves and in check
		return noLegalMoves() and self.check(team)

	# todo: need a way to check for empty matrix since legal moves is no longer a a list
	def staleMate(self, team: bool) -> bool:

		def noLegalMoves(self) -> bool:
			for r in range(8):
				for c in range(8):
					if self.legal_moves[r][c]:
						return False
			return True

		# 100 moves per side or no legal moves + no check
		return (self.cnt == 200) or (noLegalMoves() and (not self.check(team)))

	def generateControlMatrix(self) -> None:

		def inBounds(x: int) -> bool:
			return x in range(8)

		def addControl(r: int, c: int, r1: int, c1: int) -> None:
			mtx[r1][c1].append((r, c))

		mtx = [[[] for _ in range(8)] for _ in range(8)]
		for r in range(8):
			for c in range(8):
				# piece here
				if cur := self.squares[r][c]:
					match cur.__class__.__name__:
						case "Pawn":
							dr = -1 if cur.team else 1  # delta row
							if inBounds(sr := r + dr):
								if inBounds(sc := c + 1):
									addControl(r, c, sr, sc)
								if inBounds(sc := c - 1):
									addControl(r, c, sr, sc)
						case "Knight":
							# all knight moves (relative to cur pos)
							moves = ((2, 1), (2, -1), (-2, 1), (-2, -1), \
									 (1, 2), (1, -2), (-1, 2), (-1, -2))
							for m in moves:
								if inBounds(sr := r + m[0]) and inBounds(sc := c + m[1]):
									addControl(r, c, sr, sc)
						case "Bishop":
							dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all diagonal directions (relative to cur pos)
							for d in dirs:
								r1, c1 = r + d[0], c + d[1]
								while inBounds(r1) and inBounds(c1):
									addControl(r, c, r1, c1)
									# piece on this square, stop
									if self.squares[r1][c1]:
										break
									r1 += d[0]
									c1 += d[1]
						case "Rook":
							deltas = (1, -1)  # straight delta dir (relative to cur pos)
							for d in deltas:
								r1, c1 = r + d, c + d
								while inBounds(r1):
									addControl(r, c, r1, c)
									# piece on this square, stop
									if self.squares[r1][c]:
										break
									r1 += d
								while inBounds(c1):
									addControl(r, c, r, c1)
									# piece on this square, stop
									if self.squares[r][c1]:
										break
									c1 += d
						case "Queen":
							# diagonal
							dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all diagonal directions (relative to cur pos)
							for d in dirs:
								r1, c1 = r + d[0], c + d[1]
								while inBounds(r1) and inBounds(c1):
									addControl(r, c, r1, c1)
									# piece on this square, stop
									if self.squares[r1][c1]:
										break
									r1 += d[0]
									c1 += d[1]
							# straight
							deltas = (1, -1)  # straight delta dir (relative to cur pos)
							for d in deltas:
								r1, c1 = r + d, c + d
								while inBounds(r1):
									addControl(r, c, r1, c)
									# piece on this square, stop
									if self.squares[r1][c]:
										break
									r1 += d
								while inBounds(c1):
									addControl(r, c, r, c1)
									# piece on this square, stop
									if self.squares[r][c1]:
										break
									c1 += d
						case "King":
							# all king moves (ring around king pos)
							moves = ((1, 1), (1, 0), (1, -1), (0, -1), \
									 (-1, -1), (-1, 0), (-1, 1), (0, 1))
							for m in moves:
								if inBounds(sr := r + m[0]) and inBounds(sc := c + m[1]):
									addControl(r, c, sr, sc)
						case _:
							pass
		self.control_mtx = mtx

	def updateControlMatrix(self, r: int, c: int, r1: int, c1: int) -> None:
		'''
		given a move, update all relevant control squares
		- to really optimize:
			- if piece taken, remove all their control
				- not taken, need to update all pieces controlling the new square
			- then remove all rc piece's control and add to satck update all pieces controlling it's old square (in relevant directions)
			- 
		update moved for p,r,k
		'''
		'''
		if piece @ r1,c1
			remove all of its control
		else
			add all pieces controlling r1,c1 to stack
		remove rc and it's control
		add all pieces controlling r,c to to stack
		remove control of all pieces (IN RELEVANT DIRECTION), add to new stack
		move old rc -> r1c1
		add it's control
		add RELEVANT control for all pieces on stack
		move r1c1 back -> rc for modularity
		
		'''

		def inBounds(x: int) -> bool:
			return x in range(8)
		
		def removeAllControl(r: int, c: int) -> None:

			def removeControl(r: int, c: int, r1: int, c1: int) -> None:
				self.control_mtx[r1][c1].remove((r, c))
			
			match (cur := self.squares[r][c]).__class__.__name__:
				case "Pawn":
					dr = -1 if cur.team else 1  # delta row
					if inBounds(sr := r + dr):
						if inBounds(sc := c + 1):
							removeControl(r, c, sr, sc)
						if inBounds(sc := c - 1):
							removeControl(r, c, sr, sc)
				case "Knight":
					# all knight moves (relative to cur pos)
					moves = ((2, 1), (2, -1), (-2, 1), (-2, -1), \
							 (1, 2), (1, -2), (-1, 2), (-1, -2))
					for m in moves:
						if inBounds(sr := r + m[0]) and inBounds(sc := c + m[1]):
							removeControl(r, c, sr, sc)
				case "Bishop":
					dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all diagonal directions (relative to cur pos)
					for d in dirs:
						r1, c1 = r + d[0], c + d[1]
						while inBounds(r1) and inBounds(c1):
							removeControl(r, c, r1, c1)
							# piece on this square, stop
							if self.squares[r1][c1]:
								break
							r1 += d[0]
							c1 += d[1]
				case "Rook":
					deltas = (1, -1)  # straight delta dir (relative to cur pos)
					for d in deltas:
						r1, c1 = r + d, c + d
						while inBounds(r1):
							removeControl(r, c, r1, c)
							# piece on this square, stop
							if self.squares[r1][c]:
								break
							r1 += d
						while inBounds(c1):
							removeControl(r, c, r, c1)
							# piece on this square, stop
							if self.squares[r][c1]:
								break
							c1 += d
				case "Queen":
					# diagonal
					dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all diagonal directions (relative to cur pos)
					for d in dirs:
						r1, c1 = r + d[0], c + d[1]
						while inBounds(r1) and inBounds(c1):
							removeControl(r, c, r1, c1)
							# piece on this square, stop
							if self.squares[r1][c1]:
								break
							r1 += d[0]
							c1 += d[1]
					# straight
					deltas = (1, -1)  # straight delta dir (relative to cur pos)
					for d in deltas:
						r1, c1 = r + d, c + d
						while inBounds(r1):
							removeControl(r, c, r1, c)
							# piece on this square, stop
							if self.squares[r1][c]:
								break
							r1 += d
						while inBounds(c1):
							removeControl(r, c, r, c1)
							# piece on this square, stop
							if self.squares[r][c1]:
								break
							c1 += d
				case "King":
					# all king moves (ring around king pos)
					moves = ((1, 1), (1, 0), (1, -1), (0, -1), \
							 (-1, -1), (-1, 0), (-1, 1), (0, 1))
					for m in moves:
						if inBounds(sr := r + m[0]) and inBounds(sc := c + m[1]):
							removeControl(r, c, sr, sc)
				case _:
					pass

		def addAllControl(r: int, c: int) -> None:
			
			def addControl(r: int, c: int, r1: int, c1: int) -> None:
				self.control_mtx[r1][c1].append((r, c))
			
			match (cur := self.squares[r][c]).__class__.__name__:
				case "Pawn":
					dr = -1 if cur.team else 1  # delta row
					if inBounds(sr := r + dr):
						if inBounds(sc := c + 1):
							addControl(r, c, sr, sc)
						if inBounds(sc := c - 1):
							addControl(r, c, sr, sc)
				case "Knight":
					# all knight moves (relative to cur pos)
					moves = ((2, 1), (2, -1), (-2, 1), (-2, -1), \
							 (1, 2), (1, -2), (-1, 2), (-1, -2))
					for m in moves:
						if inBounds(sr := r + m[0]) and inBounds(sc := c + m[1]):
							addControl(r, c, sr, sc)
				case "Bishop":
					dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all diagonal directions (relative to cur pos)
					for d in dirs:
						r1, c1 = r + d[0], c + d[1]
						while inBounds(r1) and inBounds(c1):
							addControl(r, c, r1, c1)
							# piece on this square, stop
							if self.squares[r1][c1]:
								break
							r1 += d[0]
							c1 += d[1]
				case "Rook":
					deltas = (1, -1)  # straight delta dir (relative to cur pos)
					for d in deltas:
						r1, c1 = r + d, c + d
						while inBounds(r1):
							addControl(r, c, r1, c)
							# piece on this square, stop
							if self.squares[r1][c]:
								break
							r1 += d
						while inBounds(c1):
							addControl(r, c, r, c1)
							# piece on this square, stop
							if self.squares[r][c1]:
								break
							c1 += d
				case "Queen":
					# diagonal
					dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all diagonal directions (relative to cur pos)
					for d in dirs:
						r1, c1 = r + d[0], c + d[1]
						while inBounds(r1) and inBounds(c1):
							addControl(r, c, r1, c1)
							# piece on this square, stop
							if self.squares[r1][c1]:
								break
							r1 += d[0]
							c1 += d[1]
					# straight
					deltas = (1, -1)  # straight delta dir (relative to cur pos)
					for d in deltas:
						r1, c1 = r + d, c + d
						while inBounds(r1):
							addControl(r, c, r1, c)
							# piece on this square, stop
							if self.squares[r1][c]:
								break
							r1 += d
						while inBounds(c1):
							addControl(r, c, r, c1)
							# piece on this square, stop
							if self.squares[r][c1]:
								break
							c1 += d
				case "King":
					# all king moves (ring around king pos)
					moves = ((1, 1), (1, 0), (1, -1), (0, -1), \
							 (-1, -1), (-1, 0), (-1, 1), (0, 1))
					for m in moves:
						if inBounds(sr := r + m[0]) and inBounds(sc := c + m[1]):
							addControl(r, c, sr, sc)
				case _:
					pass

		def removeRelevantControl(r: int, c: int, rx: int, cx: int) -> None:
			
			def removeControl(r: int, c: int, r1: int, c1: int) -> None:
				self.control_mtx[r1][c1].remove((r, c))
			
			match (cur := self.squares[r][c]).__class__.__name__:
				case "Pawn":
					pass
				case "Knight":
					pass
				case "Bishop":
					dr, dc = ((1 if (rx > r) else -1), (1 if (cx > c) else -1))  # direction of r1, c1
					r1, c1 = r + dr, c + dc
					while (r1 != (rx + dr)) and (c1 != (cx + dc)):
						removeControl(r, c, r1, c1)
						r1 += dr
						c1 += dc
				case "Rook":
					# same col
					if (c1 == c):
						dr = (1 if (rx > r) else -1)
						r1 = r + dr
						while r1 != (rx + dr):
							removeControl(r, c, r1, c)
							r1 += dr
					# same row
					else:
						dc = (1 if (cx > c) else -1)
						c1 = c + dc
						while c1 != (cx + dc):
							removeControl(r, c, r, c1)
							c1 += dc
				case "Queen":
					# diagonal
					dr, dc = ((1 if (rx > r) else -1), (1 if (cx > c) else -1))  # direction of r1, c1
					r1, c1 = r + dr, c + dc
					while (r1 != (rx + dr)) and (c1 != (cx + dc)):
						removeControl(r, c, r1, c1)
						r1 += dr
						c1 += dc
					# straight
					# same col
					if (c1 == c):
						dr = (1 if (rx > r) else -1)
						r1 = r + dr
						while r1 != (rx + dr):
							removeControl(r, c, r1, c)
							r1 += dr
					# same row
					else:
						dc = (1 if (cx > c) else -1)
						c1 = c + dc
						while c1 != (cx + dc):
							removeControl(r, c, r, c1)
							c1 += dc
				case "King":
					pass
				case _:
					pass

		def addRelevantControl(r: int, c: int, rx: int, cx: int) -> None:

			def addControl(r: int, c: int, r1: int, c1: int) -> None:
				self.control_mtx[r1][c1].append((r, c))
			
			match (cur := self.squares[r][c]).__class__.__name__:
				case "Pawn":
					pass
				case "Knight":
					pass
				case "Bishop":
					dr, dc = ((1 if (rx > r) else -1), (1 if (cx > c) else -1))  # direction of r1, c1
					r1, c1 = r + dr, c + dc
					while inBounds(r1) and inBounds(c1):
						addControl(r, c, r1, c1)
						# piece on this square, stop
						if self.squares[r1][c1]:
							break
						r1 += dr
						c1 += dc
				case "Rook":
					# same col
					if (c1 == c):
						dr = (1 if (rx > r) else -1)
						r1 = r + dr
						while inBounds(r1):
							addControl(r, c, r1, c)
							# piece on this square, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
					# same row
					else:
						dc = (1 if (cx > c) else -1)
						c1 = c + dc
						while inBounds(c1):
							addControl(r, c, r, c1)
							# piece on this square, stop
							if self.squares[r1][c1]:
								break
							c1 += dc
				case "Queen":
					# diagonal
					dr, dc = ((1 if (rx > r) else -1), (1 if (cx > c) else -1))  # direction of r1, c1
					r1, c1 = r + dr, c + dc
					while inBounds(r1) and inBounds(c1):
						addControl(r, c, r1, c1)
						# piece on this square, stop
						if self.squares[r1][c1]:
							break
						r1 += dr
						c1 += dc
					# straight
					# same col
					if (c1 == c):
						dr = (1 if (rx > r) else -1)
						r1 = r + dr
						while inBounds(r1):
							addControl(r, c, r1, c)
							# piece on this square, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
					# same row
					else:
						dc = (1 if (cx > c) else -1)
						c1 = c + dc
						while inBounds(c1):
							addControl(r, c, r, c1)
							# piece on this square, stop
							if self.squares[r1][c1]:
								break
							c1 += dc
				case "King":
					pass
				case _:
					pass

		remove_rc, add_rc = [], []
		remove_r1c1, add_r1c1 = [], []
		# if piece on new square, remove its control
		if self.squares[r1][c1]:
			removeAllControl(r1, c1)
		# no piece on new square
		else:
			# add all pieces that control new square to stack
			for p in self.control_mtx[r1][c1]:
				remove_r1c1.append(p)
		# remove piece @ r,c and its control
		removeAllControl(r, c)
		piece, self.squares[r][c] = self.squares[r][c], None
		# add all pieces that control old square to remove stack
		for p in self.control_mtx[r][c]:
			remove_rc.append(p)
		# remove relevant control of all pieces controlling r,c
		while remove_rc:
			top = remove_rc.pop()
			# need to add control back later
			add_rc.append(top)
			removeRelevantControl(top[0], top[1], r, c)
		# remove relevant control of all pieces controlling r1,c1
		while remove_r1c1:
			top = remove_r1c1.pop()
			# need to add control back later
			add_r1c1.append(top)
			removeRelevantControl(top[0], top[1], r1, c1)
		# move piece
		piece_rc, piece_r1c1 = self.squares[r][c], self.squares[r1][c1]
		self.squares[r1][c1], self.squares[r][c] = piece_rc, None
		addAllControl(r1, c1)
		# add back relevant control for pieces previously controlling r,c
		while add_rc:
			top = add_rc.pop()
			addRelevantControl(top[0], top[1], r, c)
		# add back relevant control for pieces previously controlling r1,c1
		while add_r1c1:
			top = add_r1c1.pop()
			addRelevantControl(top[0], top[1], r1, c1)
		# put pieces back for modularity
		self.squares[r][c], self.squares[r1][c1] = piece_rc, piece_r1c1

	def generateLegalMoves(self, team: bool) -> None:

		def inBounds(x: int) -> bool:
			return x in range(8)
		
		def inCheckAfter(r: int, c: int, r1: int, c1: int) -> bool:
			'''
			try move r,c -> r1,c1, see if in check after
			'''
			piece_rc, piece_r1c1 = self.squares[r][c], self.squares[r1][c1]
			old_mtx = self.control_mtx
			# try move
			self.updateControlMatrix(r, c, r1, c1)
			self.squares[r][c], self.squares[r1][c1] = None, piece_rc
			if piece_rc.__class__.__name__ == "King":
				if piece_rc.team:
					self.white_king_pos = (r1, c1)
				else:
					self.black_king_pos = (r1, c1)
			check = self.check(team)  # under check after this move?
			# undo move
			# todo: need a way to undo move, restore taken piece and update control mtx
			# todo: could just store old control mtx and set it back after move
			self.undoMove((r, c, r1, c1, piece_rc, piece_r1c1, piece_rc.moved))
			self.control_mtx = old_mtx
			
			pass

		def inCheckAfter1(r: int, c: int, r1: int, c1: int) -> bool:
			'''
			try out move, see if in check afterwards
			'''
			old, old1 = self.squares[r][c], self.squares[r1][c1]
			pt = old.__class__.__name__  # piece type
			old_control_mtx = self.control_mtx
			# try move
			self.squares[r][c], self.squares[r1][c1] = None, self.squares[r][c]
			# king, update king pos
			if pt == "King":
				if old.team:
					self.white_king_pos = (r1, c1)
				else:
					self.black_king_pos = (r1, c1)
			self.generateControlMatrix()
			check = self.checkCheck(team)  # still under check after move?
			# undo move
			self.squares[r][c], self.squares[r1][c1] = old, old1
			self.control_mtx = old_control_mtx
			self.generateControlMatrix()
			# king, update king pos
			if pt == "King":
				if old.team:
					self.white_king_pos = (r, c)
				else:
					self.black_king_pos = (r, c)
			return check
			
		def addMove(r: int, c: int, r1: int, c1: int) -> None:
			legal[r][c].append((r1, c1))

		legal = []  # list of all legal moves for this team with this board
		for r in range(8):
			for c in range(8):
				# piece here and it's on this team
				if (cur := self.squares[r][c]) and (cur.team == team):
					match cur.__class__.__name__:
						case "Pawn":
							dr = -1 if team else 1  # delta row
							if inBounds(sr := r + dr): 
								# move 1
								if (self.pos_mtx[sr][c] == None) and (not inCheckAfter(r, c, sr, c)):
									addMove(r, c, sr, c)
								# capture right
								if inBounds(sc := c + 1) and (self.pos_mtx[sr][sc] == (not team)) \
									and (not inCheckAfter(r, c, sr, sc)):
									addMove(r, c, sr, sc)
								# capture left
								if inBounds(sc := c - 1) and (self.pos_mtx[sr][sc] == (not team)) \
									and (not inCheckAfter(r, c, sr, sc)):
									addMove(r, c, sr, sc)
							# move 2 (first move only)
							if inBounds(dr2 := sr + dr) and (not cur.moved) and (self.pos_mtx[sr][c] == self.pos_mtx[dr2][c] == None) \
								and not inCheckAfter(r, c, dr2, c):
								addMove(r, c, dr2, c)
						case "Knight":
							# all knight moves (relative to cur pos)
							moves = ((2, 1), (2, -1), (-2, 1), (-2, -1), \
									 (1, 2), (1, -2), (-1, 2), (-1, -2))
							for m in moves:
								if inBounds(sr := r + m[0]) and inBounds(sc := c + m[1]) and (self.pos_mtx[sr][sc] != team) \
									and (not inCheckAfter(r, c, sr, sc)):
										addMove(r, c, sr, sc)
						case "Bishop":
							dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all diagonal directions (relative to cur pos)
							for d in dirs:
								r1, c1 = r + d[0], c + d[1]
								while inBounds(r1) and inBounds(c1) and (self.pos_mtx[r1][c1] != team):
									if not inCheckAfter(r, c, r1, c1):
										addMove(r, c, r1, c1)
									# piece on this square, stop
									if self.pos_mtx[r1][c1] != None:
										break
									r1 += d[0]
									c1 += d[1]
						case "Rook":
							deltas = (1, -1)  # straight delta dir (relative to cur pos)
							for d in deltas:
								r1, c1 = r + d, c + d
								while inBounds(r1) and (self.pos_mtx[r1][c] != team):
									if not inCheckAfter(r, c, r1, c):
										addMove(r, c, r1, c)
									# piece on this square, stop
									if self.pos_mtx[r1][c] != None:
										break
									r1 += d
								while inBounds(c1) and (self.pos_mtx[r][c1] != team):
									if not inCheckAfter(r, c, r, c1):
										addMove(r, c, r, c1)
									# piece on this square, stop
									if self.pos_mtx[r][c1] != None:
										break
									c1 += d
						case "Queen":
							# diagonal
							dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all diagonal directions (relative to cur pos)
							for d in dirs:
								r1, c1 = r + d[0], c + d[1]
								while inBounds(r1) and inBounds(c1) and (self.pos_mtx[r1][c1] != team):
									if not inCheckAfter(r, c, r1, c1):
										addMove(r, c, r1, c1)
									# piece on this square, stop
									if self.pos_mtx[r1][c1] != None:
										break
									r1 += d[0]
									c1 += d[1]
							# straight
							deltas = (1, -1)
							for d in deltas:
								r1, c1 = r + d, c + d
								while inBounds(r1) and (self.pos_mtx[r1][c] != team):
									if not inCheckAfter(r, c, r1, c):
										addMove(r, c, r1, c)
									# piece on this square, stop
									if self.pos_mtx[r1][c] != None:
										break
									r1 += d
								while inBounds(c1) and (self.pos_mtx[r][c1] != team):
									if not inCheckAfter(r, c, r, c1):
										addMove(r, c, r, c1)
									# piece on this square, stop
									if self.pos_mtx[r][c1] != None:
										break
									c1 += d
						case "King":
							moves = ((1, 1), (1, 0), (1, -1), (0, -1), \
									 (-1, -1), (-1, 0), (-1, 1), (0, 1))
							for m in moves:
								# in bounds and my team not on new pos and no opp pieces control new pos and not in check after move
								if inBounds(sr := r + m[0]) and inBounds(sc := c + m[1]) \
									and (self.pos_mtx[sr][sc] != team) and (not any([(p[2] != team) for p in self.control_mtx[sr][sc]])) \
									and (not inCheckAfter(r, c, sr, sc)):
										addMove(r, c, sr, sc)
							# castle
							if (not cur.moved):
								# short
								if ((rook := self.squares[r][7]) != None) and (rook.__class__.__name__ == "Rook") and (not rook.moved) \
									and (self.squares[r][5] == self.squares[r][6] == None) and (not inCheckAfter(r, 4, r, 6)):
										addMove(r, 4, r, 6)
								# long
								if ((rook := self.squares[r][0]) != None) and (rook.__class__.__name__ == "Rook") and (not rook.moved) \
									and (self.squares[r][1] == self.squares[r][2] == self.squares[r][3] == None) \
										and (not inCheckAfter(r, 4, r, 2)):
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
				cur = self.squares[r][c]
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
