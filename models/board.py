from models.pieces import Pawn, Knight, Bishop, Rook, Queen, King

class Board:
	def __init__(self):
		self.initBoard()
		# pos_mtx: binary/null matrix that contains info about what team each piece is on
		# control_mtx: matrix that contains info about what pieces control what squares (both teams)
		# legal_moves: matrix that contains all legal moves for cur pos (only cur team)
	
	def initBoard(self):
		self.squares = [[None for _ in range(8)] for _ in range (8)]
		# pawns (black, white)
		for c in range(8):
			self.squares[1][c], self.squares[6][c] = Pawn(False), Pawn(True)
		# pieces (black, white)
		self.squares[0][0], self.squares[7][0] = Rook(False), Rook(True)
		self.squares[0][1], self.squares[7][1] = Knight(False), Knight(True)
		self.squares[0][2], self.squares[7][2] = Bishop(False), Bishop(True)
		self.squares[0][3], self.squares[7][3] = Queen(False), Queen(True)
		self.squares[0][4], self.squares[7][4] = King(False), King(True)
		self.squares[0][5], self.squares[7][5] = Bishop(False), Bishop(True)
		self.squares[0][6], self.squares[7][6] = Knight(False), Knight(True)
		self.squares[0][7], self.squares[7][7] = Rook(False), Rook(True)
		# king pos
		self.black_king_pos, self.white_king_pos = (0, 4), (7, 4)
		# generate matrices
		self.generateControlMatrix()
		self.generatePositionMatrix()
		self.generateLegalMoves(True)

	def move(self, r: int, c: int, rx: int, cx: int) -> None:
		'''
		move piece @ r,c -> rx,cx
		'''
		move = (r, c, rx, cx)
		piece = self.squares[r][c]
		king = piece.__class__.__name__ == "King"  # p1 is king bool
		# short castle
		if king and (move in ((0, 4, 0, 6), (7, 4, 7, 6))):
			# set both king and rook moved to true
			piece.moved, self.squares[r][7].moved = True, True  # could do this with a = b = True
			# move king + rook
			self.squares[r][4], self.squares[r][6] = None, piece
			self.squares[r][7], self.squares[r][5] = None, self.squares[r][7]
		# long castle
		elif king and (move in ((0, 4, 0, 2), (7, 4, 7, 2))):
			# set both king and rook moved to true
			piece.moved, self.squares[r][0].moved = True, True  # could do this with a = b = True
			# move king + rook
			self.squares[r][4], self.squares[r][2] = None, piece
			self.squares[r][0], self.squares[r][3] = None, self.squares[r][0]
		# other moves
		else:
			self.squares[r][c], self.squares[rx][cx] = None, piece
			if hasattr(piece, "moved"):
				piece.moved = True
		# update king pos
		if king:
			if piece.team:
				self.white_king_pos = (rx, cx)
			else:
				self.black_king_pos = (rx, cx)
	
	def undoMove(self, r: int, c: int, rx: int, cx: int, p1: object, p2: object, p1_moved: bool) -> None:
		'''
		undo given move
		'''		
		move = (r, c, rx, cx)
		king = p1.__class__.__name__ == "King"  # p1 is king bool
		# short castle
		if king and (move in ((0, 4, 0, 6), (7, 4, 7, 6))):
			self.squares[r][4], self.squares[r][7] = self.squares[r][6], self.squares[r][5]
			self.squares[r][5] = self.squares[r][6] = None
			p1.moved = False
			self.squares[r][7].moved = False
		# long castle
		elif king and (move in ((0, 4, 0, 2), (7, 4, 7, 2))):
			self.squares[r][4], self.squares[r][0] = self.squares[r][2], self.squares[r][3]
			self.squares[r][1] = self.squares[r][2] = self.squares[r][3] = None
			self.squares[r][4].moved = False
			self.squares[r][0].moved = False
		# other move
		else:
			self.squares[r][c], self.squares[rx][cx] = p1, p2
			if hasattr(p1, "moved"):
				p1.moved = p1_moved
		if king:
			# revert king pos
			if p1.team:
				self.white_king_pos = (r, c)
			else:
				self.black_king_pos = (r, c)

	def humanMove(self, r: int, c: int, rx: int, cx: int) -> None:
		'''
		precondition: move is legal
		'''

		def promote() -> str:
			# promote pawn if on last rank
			inp = None
			while inp not in ("Knight", "Bishop", "Rook", "Queen"):
				inp = input("promote pawn to ... (\"Knight\", \"Bishop\", \"Rook\", \"Queen\")\n").strip()
			return inp
		
		# update board state
		self.updateControlMatrix(r, c, rx, cx)
		self.updatePositionMatrix(r, c, rx, cx)
		self.move(r, c, rx, cx)
		# promote
		if ((cur := self.squares[rx][cx]).__class__.__name__ == "Pawn") and (rx in (0, 7)):
			match promote():
				case "Pawn":
					pass
				case "Knight":
					self.squares[rx][cx] = Knight(cur.team)
				case "Bishop":
					self.squares[rx][cx] = Bishop(cur.team)
				case "Rook":
					self.squares[rx][cx] = Rook(cur.team)
					self.squares.moved = True
				case "Queen":
					self.squares[rx][cx] = Queen(cur.team)

	def botMove(self, r: int, c: int, rx: int, cx: int) -> None:
		# update board state
		self.updateControlMatrix(r, c, rx, cx)
		self.updatePositionMatrix(r, c, rx, cx)
		self.move(r, c, rx, cx)
		# auto promote to queen
		if ((cur := self.squares[rx][cx]).__class__.__name__ == "Pawn") and (rx in (0, 7)):
			self.squares[rx][cx] = Queen(cur.team)

	def check(self, team: bool) -> bool:
		'''
		if the given team is currently in check
		'''

		def controls(r: int, c: int, team: bool):
			for p in self.control_mtx[r][c]:
				pr, pc = p
				if self.pos_mtx[pr][pc] == team:
					return True
			return False

		r, c = self.white_king_pos if team else self.black_king_pos
		return controls(r, c, not team)
	
	def stalemate(self, team: bool, move_cnt: int) -> bool:
		'''
		if the given team is stalemated
		'''

		def noLegalMoves() -> bool:
			for r in range(8):
				for c in range(8):
					if self.legal_moves[r][c]:
						return False
			return True

		return (move_cnt == 200) or ((not self.check(team)) and noLegalMoves())
	
	def checkmate(self, team: bool) -> bool:
		'''
		if the given team is checkmated
		'''

		def noLegalMoves() -> bool:
			for r in range(8):
				for c in range(8):
					if self.legal_moves[r][c]:
						return False
			return True

		return self.check(team) and noLegalMoves()
	
	def generatePositionMatrix(self) -> None:
		'''
		generate binary/null matrix that contains info about what team each piece is on
		'''

		mtx = [[None for _ in range(8)] for _ in range(8)]
		for r in range(8):
			for c in range(8):
				if cur := self.squares[r][c]:
					mtx[r][c] = cur.team
		self.pos_mtx = mtx

	def updatePositionMatrix(self, r: int, c: int, rx: int, cx: int) -> None:
		self.pos_mtx[r][c], self.pos_mtx[rx][cx] = None, self.pos_mtx[r][c]

	def revertPositionMatrix(self, r: int, c: int, rx: int, cx: int, p1_team: bool, p2_team: bool) -> None:
		self.pos_mtx[r][c], self.pos_mtx[rx][cx] = p1_team, p2_team

	def generateControlMatrix(self) -> None:
		'''
		generate matrix that contains info about all squares under control/attack (both teams)
		'''

		def inBounds(x: int) -> bool:
			return x in range(8)

		def addControl(r: int, c: int, rx: int, cx: int) -> None:
			mtx[rx][cx].append((r, c))

		mtx = [[[] for _ in range(8)] for _ in range(8)]
		for r in range(8):
			for c in range(8):
				# piece here
				if cur := self.squares[r][c]:
					# for each piece, go in all directions and mark each tile as their coord
					match cur.__class__.__name__:
						case "Pawn":
							dr = -1 if cur.team else 1  # delta row
							if inBounds(r1 := r + dr):
								# capture left
								if inBounds(c1 := c - 1):
									addControl(r, c, r1, c1)
								# capture right
								if inBounds(c1 := c + 1):
									addControl(r, c, r1, c1)
						case "Knight":
							moves = ((1, 2), (1, -2), (-1, 2), (-1, -2),
									 (2, 1), (2, -1), (-2, 1), (-2, -1))  # all legal moves (relative to cur pos)
							for m in moves:
								dr, dc = m  # delta row, col
								if inBounds(r1 := r + dr) and inBounds(c1 := c + dc):
									addControl(r, c, r1, c1)
						case "Bishop":
							dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all directions (relative)
							for d in dirs:
								dr, dc = d  # delta row, col
								r1, c1 = r + dr, c + dc
								while inBounds(r1) and inBounds(c1):
									addControl(r, c, r1, c1)
									# piece here, stop
									if self.squares[r1][c1]:
										break
									r1 += dr
									c1 += dc
						case "Rook":
							dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
							for d in dirs:
								dr, dc = d  # delta row, col
								# same col
								if dr:
									r1 = r + dr
									while inBounds(r1):
										addControl(r, c, r1, c)
										# piece here, stop
										if self.squares[r1][c]:
											break
										r1 += dr
								# same row
								else:
									c1 = c + dc
									while inBounds(c1):
										addControl(r, c, r, c1)
										# piece here, stop
										if self.squares[r][c1]:
											break
										c1 += dc
						case "Queen":
							# diagonals
							dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all directions (relative)
							for d in dirs:
								dr, dc = d  # delta row, col
								r1, c1 = r + dr, c + dc
								while inBounds(r1) and inBounds(c1):
									addControl(r, c, r1, c1)
									# piece here, stop
									if self.squares[r1][c1]:
										break
									r1 += dr
									c1 += dc
							# straights
							dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
							for d in dirs:
								dr, dc = d  # delta row, col
								# same col
								if dr:
									r1 = r + dr
									while inBounds(r1):
										addControl(r, c, r1, c)
										# piece here, stop
										if self.squares[r1][c]:
											break
										r1 += dr
								# same row
								else:
									c1 = c + dc
									while inBounds(c1):
										addControl(r, c, r, c1)
										# piece here, stop
										if self.squares[r][c1]:
											break
										c1 += dc
						case "King":
							moves = ((1, 1), (-1, -1), (1, 0), (-1, 0),
									 (0, 1), (0, -1), (1, -1), (-1, 1))  # all legal moves (relative to cur pos)
							for m in moves:
								dr, dc = m  # delta row, col
								if inBounds(r1 := r + dr) and inBounds(c1 := c + dc):
									addControl(r, c, r1, c1)
						case _:
							pass
		self.control_mtx = mtx

	def updateControlMatrix(self, r: int, c: int, rx: int, cx: int) -> None:
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

			def removeControl(r: int, c: int, rx: int, cx: int) -> None:
				if (r, c) in self.control_mtx[rx][cx]:
					self.control_mtx[rx][cx].remove((r, c))
			
			match (cur := self.squares[r][c]).__class__.__name__:
				case "Pawn":
					dr = -1 if cur.team else 1  # delta row
					if inBounds(r1 := r + dr):
						# capture left
						if inBounds(c1 := c - 1):
							removeControl(r, c, r1, c1)
						# capture right
						if inBounds(c1 := c + 1):
							removeControl(r, c, r1, c1)
				case "Knight":
					moves = ((1, 2), (1, -2), (-1, 2), (-1, -2),
							 (2, 1), (2, -1), (-2, 1), (-2, -1))  # all legal moves (relative to cur pos)
					for m in moves:
						dr, dc = m  # delta row, col
						if inBounds(r1 := r + dr) and inBounds(c1 := c + dc):
							removeControl(r, c, r1, c1)
				case "Bishop":
					dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						r1, c1 = r + dr, c + dc
						while inBounds(r1) and inBounds(c1):
							removeControl(r, c, r1, c1)
							# piece here, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
							c1 += dc
				case "Rook":
					dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						# same col
						if dr:
							r1 = r + dr
							while inBounds(r1):
								removeControl(r, c, r1, c)
								# piece here, stop
								if self.squares[r1][c]:
									break
								r1 += dr
						# same row
						else:
							c1 = c + dc
							while inBounds(c1):
								removeControl(r, c, r, c1)
								# piece here, stop
								if self.squares[r][c1]:
									break
								c1 += dc
				case "Queen":
					# diagonals
					dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						r1, c1 = r + dr, c + dc
						while inBounds(r1) and inBounds(c1):
							removeControl(r, c, r1, c1)
							# piece here, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
							c1 += dc
					# straights
					dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						# same col
						if dr:
							r1 = r + dr
							while inBounds(r1):
								removeControl(r, c, r1, c)
								# piece here, stop
								if self.squares[r1][c]:
									break
								r1 += dr
						# same row
						else:
							c1 = c + dc
							while inBounds(c1):
								removeControl(r, c, r, c1)
								# piece here, stop
								if self.squares[r][c1]:
									break
								c1 += dc
				case "King":
					moves = ((1, 1), (-1, -1), (1, 0), (-1, 0),
							 (0, 1), (0, -1), (1, -1), (-1, 1))  # all legal moves (relative to cur pos)
					for m in moves:
						dr, dc = m  # delta row, col
						if inBounds(r1 := r + dr) and inBounds(c1 := c + dc):
							removeControl(r, c, r1, c1)
				case _:
					pass

		def removeRelevantControl(r: int, c: int, rx: int, cx: int) -> None:
			
			def removeControl(r: int, c: int, rx: int, cx: int) -> None:
				if (r, c) in self.control_mtx[rx][cx]:
					self.control_mtx[rx][cx].remove((r, c))
			
			match self.squares[r][c].__class__.__name__:
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
					if (cx == c):
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
					if (cx != c) and (rx != c):
						dr, dc = ((1 if (rx > r) else -1), (1 if (cx > c) else -1))  # direction of r1, c1
						r1, c1 = r + dr, c + dc
						while (r1 != (rx + dr)) and (c1 != (cx + dc)):
							removeControl(r, c, r1, c1)
							r1 += dr
							c1 += dc
					# straight
					# same col
					elif (cx == c):
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

		def addAllControl(r: int, c: int) -> None:

			def addControl(r: int, c: int, rx: int, cx: int) -> None:
				if (r, c) not in self.control_mtx[rx][cx]:
					self.control_mtx[rx][cx].append((r, c))

			match (cur := self.squares[r][c]).__class__.__name__:
				case "Pawn":
					dr = -1 if cur.team else 1  # delta row
					if inBounds(r1 := r + dr):
						# capture left
						if inBounds(c1 := c - 1):
							addControl(r, c, r1, c1)
						# capture right
						if inBounds(c1 := c + 1):
							addControl(r, c, r1, c1)
				case "Knight":
					moves = ((1, 2), (1, -2), (-1, 2), (-1, -2),
							 (2, 1), (2, -1), (-2, 1), (-2, -1))  # all legal moves (relative to cur pos)
					for m in moves:
						dr, dc = m  # delta row, col
						if inBounds(r1 := r + dr) and inBounds(c1 := c + dc):
							addControl(r, c, r1, c1)
				case "Bishop":
					dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						r1, c1 = r + dr, c + dc
						while inBounds(r1) and inBounds(c1):
							addControl(r, c, r1, c1)
							# piece here, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
							c1 += dc
				case "Rook":
					dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						# same col
						if dr:
							r1 = r + dr
							while inBounds(r1):
								addControl(r, c, r1, c)
								# piece here, stop
								if self.squares[r1][c]:
									break
								r1 += dr
						# same row
						else:
							c1 = c + dc
							while inBounds(c1):
								addControl(r, c, r, c1)
								# piece here, stop
								if self.squares[r][c1]:
									break
								c1 += dc
				case "Queen":
					# diagonals
					dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						r1, c1 = r + dr, c + dc
						while inBounds(r1) and inBounds(c1):
							addControl(r, c, r1, c1)
							# piece here, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
							c1 += dc
					# straights
					dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						# same col
						if dr:
							r1 = r + dr
							while inBounds(r1):
								addControl(r, c, r1, c)
								# piece here, stop
								if self.squares[r1][c]:
									break
								r1 += dr
						# same row
						else:
							c1 = c + dc
							while inBounds(c1):
								addControl(r, c, r, c1)
								# piece here, stop
								if self.squares[r][c1]:
									break
								c1 += dc
				case "King":
					moves = ((1, 1), (-1, -1), (1, 0), (-1, 0),
							 (0, 1), (0, -1), (1, -1), (-1, 1))  # all legal moves (relative to cur pos)
					for m in moves:
						dr, dc = m  # delta row, col
						if inBounds(r1 := r + dr) and inBounds(c1 := c + dc):
							addControl(r, c, r1, c1)
				case _:
					pass

		def addRelevantControl(r: int, c: int, rx: int, cx: int) -> None:
			
			def addControl(r: int, c: int, rx: int, cx: int) -> None:
				if (r, c) not in self.control_mtx[rx][cx]:
					self.control_mtx[rx][cx].append((r, c))
			
			match self.squares[r][c].__class__.__name__:
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
					if (cx == c):
						dr = (1 if (rx > r) else -1)
						r1 = r + dr
						while inBounds(r1):
							addControl(r, c, r1, c)
							# piece on this square, stop
							if self.squares[r1][c]:
								break
							r1 += dr
					# same row
					else:
						dc = (1 if (cx > c) else -1)
						c1 = c + dc
						while inBounds(c1):
							addControl(r, c, r, c1)
							# piece on this square, stop
							if self.squares[r][c1]:
								break
							c1 += dc
				case "Queen":
					# diagonal
					if (cx != c) and (rx != c):
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
					elif (cx == c):
						dr = (1 if (rx > r) else -1)
						r1 = r + dr
						while inBounds(r1):
							addControl(r, c, r1, c)
							# piece on this square, stop
							if self.squares[r1][c]:
								break
							r1 += dr
					# same row
					else:
						dc = (1 if (cx > c) else -1)
						c1 = c + dc
						while inBounds(c1):
							addControl(r, c, r, c1)
							# piece on this square, stop
							if self.squares[r][c1]:
								break
							c1 += dc
				case "King":
					pass
				case _:
					pass

		# stacks for r,c and rx,cx of pieces that need their relevant control removed/added back
		remove, add = [], []
		remove_x, add_x = [], []
		p1, p2 = self.squares[r][c], self.squares[rx][cx]  # piece and (possible) piece being captured
		p1_moved = p1.moved if hasattr(p1, "moved") else None
		# capturing piece
		if self.squares[rx][cx]:
			removeAllControl(rx, cx)
		else:
			# all pieces controlling rc,rx need to have their control updated
			for p in self.control_mtx[rx][cx]:
				remove_x.append(p)
		# all pieces controlling r,c need to have their control updated
		for p in self.control_mtx[r][c]:
			remove.append(p)
		# remove all of piece 1's control
		removeAllControl(r, c)
		# remove relevant control of affected pieces
		while remove:
			top = r1, c1 = remove.pop()
			add.append(top)
			removeRelevantControl(r1, c1, r, c)
		while remove_x:
			top = r1, c1 = remove_x.pop()
			add_x.append(top)
			removeRelevantControl(r1, c1, rx, cx)
		# (temporarily) move p1 to rx,cx
		self.move(r, c, rx, cx)
		# add back all control
		addAllControl(rx, cx)
		while add:
			r1, c1 = add.pop()
			addRelevantControl(r1, c1, r, c)
		while add_x:
			r1, c1 = add_x.pop()
			addRelevantControl(r1, c1, r, c)
		# move p1 back for modularity
		self.undoMove(r, c, rx, cx, p1, p2, p1_moved)

	def revertControlMatrix(self, r: int, c: int, rx: int, cx: int, p1: object, p2: object, p1_moved: bool) -> None:
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
		if piece2 is None
			(rx,cx)
			add all pieces to have relevant control removed to stack
		add all pieces targeting rc to relevant remove stack
		remove rx,cx control
		remove relevant control from everything, move to add
		undo move r,c,rx,cx
		add all control to rc
		add relevant control back to everything
		re-move r,c,rx,cx
		'''

		def inBounds(x: int) -> bool:
			return x in range(8)

		def removeAllControl(r: int, c: int) -> None:

			def removeControl(r: int, c: int, rx: int, cx: int) -> None:
				if (r, c) in self.control_mtx[rx][cx]:
					self.control_mtx[rx][cx].remove((r, c))
			
			match (cur := self.squares[r][c]).__class__.__name__:
				case "Pawn":
					dr = -1 if cur.team else 1  # delta row
					if inBounds(r1 := r + dr):
						# capture left
						if inBounds(c1 := c - 1):
							removeControl(r, c, r1, c1)
						# capture right
						if inBounds(c1 := c + 1):
							removeControl(r, c, r1, c1)
				case "Knight":
					moves = ((1, 2), (1, -2), (-1, 2), (-1, -2),
							 (2, 1), (2, -1), (-2, 1), (-2, -1))  # all legal moves (relative to cur pos)
					for m in moves:
						dr, dc = m  # delta row, col
						if inBounds(r1 := r + dr) and inBounds(c1 := c + dc):
							removeControl(r, c, r1, c1)
				case "Bishop":
					dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						r1, c1 = r + dr, c + dc
						while inBounds(r1) and inBounds(c1):
							removeControl(r, c, r1, c1)
							# piece here, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
							c1 += dc
				case "Rook":
					dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						# same col
						if dr:
							r1 = r + dr
							while inBounds(r1):
								removeControl(r, c, r1, c)
								# piece here, stop
								if self.squares[r1][c]:
									break
								r1 += dr
						# same row
						else:
							c1 = c + dc
							while inBounds(c1):
								removeControl(r, c, r, c1)
								# piece here, stop
								if self.squares[r][c1]:
									break
								c1 += dc
				case "Queen":
					# diagonals
					dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						r1, c1 = r + dr, c + dc
						while inBounds(r1) and inBounds(c1):
							removeControl(r, c, r1, c1)
							# piece here, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
							c1 += dc
					# straights
					dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						# same col
						if dr:
							r1 = r + dr
							while inBounds(r1):
								removeControl(r, c, r1, c)
								# piece here, stop
								if self.squares[r1][c]:
									break
								r1 += dr
						# same row
						else:
							c1 = c + dc
							while inBounds(c1):
								removeControl(r, c, r, c1)
								# piece here, stop
								if self.squares[r][c1]:
									break
								c1 += dc
				case "King":
					moves = ((1, 1), (-1, -1), (1, 0), (-1, 0),
							 (0, 1), (0, -1), (1, -1), (-1, 1))  # all legal moves (relative to cur pos)
					for m in moves:
						dr, dc = m  # delta row, col
						if inBounds(r1 := r + dr) and inBounds(c1 := c + dc):
							removeControl(r, c, r1, c1)
				case _:
					pass

		def removeRelevantControl(r: int, c: int, rx: int, cx: int) -> None:
			
			def removeControl(r: int, c: int, rx: int, cx: int) -> None:
				if (r, c) in self.control_mtx[rx][cx]:
					self.control_mtx[rx][cx].remove((r, c))
			
			match self.squares[r][c].__class__.__name__:
				case "Pawn":
					pass
				case "Knight":
					pass
				case "Bishop":
					dr, dc = ((1 if (rx > r) else -1), (1 if (cx > c) else -1))  # direction of r1, c1
					r1, c1 = r + dr, c + dc
					while inBounds(r1) and inBounds(c1):
						removeControl(r, c, r1, c1)
						# piece on this square, stop
						if self.squares[r1][c1]:
							break
						r1 += dr
						c1 += dc
				case "Rook":
					# same col
					if (cx == c):
						dr = (1 if (rx > r) else -1)
						r1 = r + dr
						while inBounds(r1):
							removeControl(r, c, r1, c)
							# piece on this square, stop
							if self.squares[r1][c]:
								break
							r1 += dr
					# same row
					else:
						dc = (1 if (cx > c) else -1)
						c1 = c + dc
						while inBounds(c1):
							removeControl(r, c, r, c1)
							# piece on this square, stop
							if self.squares[r][c1]:
								break
							c1 += dc
				case "Queen":
					# diagonal
					if (cx != c) and (rx != c):
						dr, dc = ((1 if (rx > r) else -1), (1 if (cx > c) else -1))  # direction of r1, c1
						r1, c1 = r + dr, c + dc
						while inBounds(r1) and inBounds(c1):
							removeControl(r, c, r1, c1)
							# piece on this square, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
							c1 += dc
					# straight
					# same col
					elif (cx == c):
						dr = (1 if (rx > r) else -1)
						r1 = r + dr
						while inBounds(r1):
							removeControl(r, c, r1, c)
							# piece on this square, stop
							if self.squares[r1][c]:
								break
							r1 += dr
					# same row
					else:
						dc = (1 if (cx > c) else -1)
						c1 = c + dc
						while inBounds(c1):
							removeControl(r, c, r, c1)
							# piece on this square, stop
							if self.squares[r][c1]:
								break
							c1 += dc
				case "King":
					pass
				case _:
					pass

		def addAllControl(r: int, c: int) -> None:

			def addControl(r: int, c: int, rx: int, cx: int) -> None:
				if (r, c) not in self.control_mtx[rx][cx]:
					self.control_mtx[rx][cx].append((r, c))

			match (cur := self.squares[r][c]).__class__.__name__:
				case "Pawn":
					dr = -1 if cur.team else 1  # delta row
					if inBounds(r1 := r + dr):
						# capture left
						if inBounds(c1 := c - 1):
							addControl(r, c, r1, c1)
						# capture right
						if inBounds(c1 := c + 1):
							addControl(r, c, r1, c1)
				case "Knight":
					moves = ((1, 2), (1, -2), (-1, 2), (-1, -2),
							 (2, 1), (2, -1), (-2, 1), (-2, -1))  # all legal moves (relative to cur pos)
					for m in moves:
						dr, dc = m  # delta row, col
						if inBounds(r1 := r + dr) and inBounds(c1 := c + dc):
							addControl(r, c, r1, c1)
				case "Bishop":
					dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						r1, c1 = r + dr, c + dc
						while inBounds(r1) and inBounds(c1):
							addControl(r, c, r1, c1)
							# piece here, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
							c1 += dc
				case "Rook":
					dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						# same col
						if dr:
							r1 = r + dr
							while inBounds(r1):
								addControl(r, c, r1, c)
								# piece here, stop
								if self.squares[r1][c]:
									break
								r1 += dr
						# same row
						else:
							c1 = c + dc
							while inBounds(c1):
								addControl(r, c, r, c1)
								# piece here, stop
								if self.squares[r][c1]:
									break
								c1 += dc
				case "Queen":
					# diagonals
					dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						r1, c1 = r + dr, c + dc
						while inBounds(r1) and inBounds(c1):
							addControl(r, c, r1, c1)
							# piece here, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
							c1 += dc
					# straights
					dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
					for d in dirs:
						dr, dc = d  # delta row, col
						# same col
						if dr:
							r1 = r + dr
							while inBounds(r1):
								addControl(r, c, r1, c)
								# piece here, stop
								if self.squares[r1][c]:
									break
								r1 += dr
						# same row
						else:
							c1 = c + dc
							while inBounds(c1):
								addControl(r, c, r, c1)
								# piece here, stop
								if self.squares[r][c1]:
									break
								c1 += dc
				case "King":
					moves = ((1, 1), (-1, -1), (1, 0), (-1, 0),
							 (0, 1), (0, -1), (1, -1), (-1, 1))  # all legal moves (relative to cur pos)
					for m in moves:
						dr, dc = m  # delta row, col
						if inBounds(r1 := r + dr) and inBounds(c1 := c + dc):
							addControl(r, c, r1, c1)
				case _:
					pass

		def addRelevantControl(r: int, c: int, rx: int, cx: int) -> None:
			
			def addControl(r: int, c: int, rx: int, cx: int) -> None:
				if (r, c) not in self.control_mtx[rx][cx]:
					self.control_mtx[rx][cx].append((r, c))
			
			match self.squares[r][c].__class__.__name__:
				case "Pawn":
					pass
				case "Knight":
					pass
				case "Bishop":
					dr, dc = ((1 if (rx > r) else -1), (1 if (cx > c) else -1))  # direction of r1, c1
					r1, c1 = r + dr, c + dc
					while (r1 != (rx + dr)) and (c1 != (cx + dc)):
						addControl(r, c, r1, c1)
						r1 += dr
						c1 += dc
				case "Rook":
					# same col
					if (cx == c):
						dr = (1 if (rx > r) else -1)
						r1 = r + dr
						while r1 != (rx + dr):
							addControl(r, c, r1, c)
							r1 += dr
					# same row
					else:
						dc = (1 if (cx > c) else -1)
						c1 = c + dc
						while c1 != (cx + dc):
							addControl(r, c, r, c1)
							c1 += dc
				case "Queen":
					# diagonal
					if (cx != c) and (rx != c):
						dr, dc = ((1 if (rx > r) else -1), (1 if (cx > c) else -1))  # direction of r1, c1
						r1, c1 = r + dr, c + dc
						while (r1 != (rx + dr)) and (c1 != (cx + dc)):
							addControl(r, c, r1, c1)
							r1 += dr
							c1 += dc
					# straight
					# same col
					elif (cx == c):
						dr = (1 if (rx > r) else -1)
						r1 = r + dr
						while r1 != (rx + dr):
							addControl(r, c, r1, c)
							r1 += dr
					# same row
					else:
						dc = (1 if (cx > c) else -1)
						c1 = c + dc
						while c1 != (cx + dc):
							addControl(r, c, r, c1)
							c1 += dc
				case "King":
					pass
				case _:
					pass

		# stacks for r,c and rx,cx of pieces that need their relevant control removed/added back
		remove, add = [], []
		remove_x, add_x = [], []
		# not a capture
		if not p2:
			for p in self.control_mtx[rx][cx]:
				remove_x.append(p)
		for p in self.control_mtx[r][c]:
			remove.append(p)
		# remove all relevant control of affected pieces
		removeAllControl(rx, cx)
		while remove:
			top = r1, c1 = remove.pop()
			add.append(top)
			removeRelevantControl(r1, c1, r, c)
		while remove_x:
			top = r1, c1 = remove_x.pop()
			add_x.append(top)
			removeRelevantControl(r1, c1, rx, cx)
		# (temporarily) undo move
		self.undoMove(r, c, rx, cx, p1, p2, p1_moved)
		# add relevant control back for affected pieces
		addAllControl(r, c)
		while add:
			r1, c1 = add.pop()
			addRelevantControl(r1, c1, r, c)
		while add_x:
			r1, c1 = add_x.pop()
			addRelevantControl(r1, c1, rx, cx)
		# redo move for modularity
		self.move(r, c, rx, cx) 

	def generateLegalMoves(self, team: bool) -> None:
		'''
		generate matrix that contains all legal moves for given team with cur pos
		'''

		def inBounds(x: int) -> bool:
			return x in range(8)

		def addMove(r: int, c: int, rx: int, cx: int) -> None:
			mtx[rx][cx].append((r, c))

		def inCheckAfter(r: int, c: int, rx: int, cx: int) -> bool:
			# store relevant info before trying move
			p1, p2 = self.squares[r][c], self.squares[rx][cx]
			p1_moved = p1.moved if hasattr(p1, "moved") else None
			p2_team = p2.team if hasattr(p2, "team") else None
			# try move
			self.updateControlMatrix(r, c, rx, cx)
			self.updatePositionMatrix(r, c, rx, cx)
			self.move(r, c, rx, cx)
			# in check after move?
			check = self.check(team)
			# undo move
			self.revertControlMatrix(r, c, rx, cx, p1, p2, p1_moved)
			self.revertPositionMatrix(r, c, rx, cx, p1.team, p2_team)
			self.undoMove(r, c, rx, cx, p1, p2, p1_moved)
			return check

		mtx = [[[] for _ in range(8)] for _ in range(8)]
		for r in range(8):
			for c in range(8):
				# piece here
				if (cur := self.squares[r][c]) and (cur.team == team):
					# for each piece, go in all directions and mark each tile as their coord
					match cur.__class__.__name__:
						case "Pawn":
							dr = -1 if cur.team else 1  # delta row
							if inBounds(r1 := r + dr):
								# push 1
								if not self.squares[r1][c] and (not inCheckAfter(r, c, r1, c)):
									addMove(r, c, r1, c)
									# push 2 (first push only)
									if inBounds(r2 := r1 + dr) and (not cur.moved) and \
										(not self.squares[r2][c]) and (not inCheckAfter(r, c, r2, c)):
										addMove(r, c, r2, c)
								# capture left
								if inBounds(c1 := c - 1) and (self.pos_mtx[r1][c1] == (not team)) \
									and (not inCheckAfter(r, c, r1, c1)):
									addMove(r, c, r1, c1)
								# capture right
								if inBounds(c1 := c + 1) and (self.pos_mtx[r1][c1] == (not team)) \
									and (not inCheckAfter(r, c, r1, c1)):
									addMove(r, c, r1, c1)
						case "Knight":
							moves = ((1, 2), (1, -2), (-1, 2), (-1, -2),
									 (2, 1), (2, -1), (-2, 1), (-2, -1))  # all legal moves (relative to cur pos)
							for m in moves:
								dr, dc = m  # delta row, col
								if inBounds(r1 := r + dr) and inBounds(c1 := c + dc) and \
									(self.pos_mtx[r1][c1] != team) and ((r, c) in self.control_mtx[r1][c1]) \
										and (not inCheckAfter(r, c, r1, c1)):
									addMove(r, c, r1, c1)
						case "Bishop":
							dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all directions (relative)
							for d in dirs:
								dr, dc = d  # delta row, col
								r1, c1 = r + dr, c + dc
								while inBounds(r1) and inBounds(c1) and (self.pos_mtx[r1][c1] != team) \
									and ((r, c) in self.control_mtx[r1][c1]) and (not inCheckAfter(r, c, r1, c1)):
									addMove(r, c, r1, c1)
									# piece here, stop
									if self.squares[r1][c1]:
										break
									r1 += dr
									c1 += dc
						case "Rook":
							dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
							for d in dirs:
								dr, dc = d  # delta row, col
								# same col
								if dr:
									r1 = r + dr
									while inBounds(r1) and (self.pos_mtx[r1][c] != team) and ((r, c) in self.control_mtx[r1][c]) \
										and (not inCheckAfter(r, c, r1, c)):
										addMove(r, c, r1, c)
										# piece here, stop
										if self.squares[r1][c]:
											break
										r1 += dr
								# same row
								else:
									c1 = c + dc
									while inBounds(c1) and (self.pos_mtx[r][c1] != team) and ((r, c) in self.control_mtx[r][c1]) \
										and (not inCheckAfter(r, c, r, c1)):
										addMove(r, c, r, c1)
										# piece here, stop
										if self.squares[r][c1]:
											break
										c1 += dc
						case "Queen":
							# diagonals
							dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all directions (relative)
							for d in dirs:
								dr, dc = d  # delta row, col
								r1, c1 = r + dr, c + dc
								while inBounds(r1) and inBounds(c1) and (self.pos_mtx[r1][c1] != team) \
									and ((r, c) in self.control_mtx[r1][c1]) and (not inCheckAfter(r, c, r1, c1)):
									addMove(r, c, r1, c1)
									# piece here, stop
									if self.squares[r1][c1]:
										break
									r1 += dr
									c1 += dc
							# straights
							dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
							for d in dirs:
								dr, dc = d  # delta row, col
								# same col
								if dr:
									r1 = r + dr
									while inBounds(r1) and (self.pos_mtx[r1][c] != team) and ((r, c) in self.control_mtx[r1][c]) \
										and (not inCheckAfter(r, c, r1, c)):
										addMove(r, c, r1, c)
										# piece here, stop
										if self.squares[r1][c]:
											break
										r1 += dr
								# same row
								else:
									c1 = c + dc
									while inBounds(c1) and (self.pos_mtx[r][c1] != team) and ((r, c) in self.control_mtx[r][c1]) \
										and (not inCheckAfter(r, c, r, c1)):
										addMove(r, c, r, c1)
										# piece here, stop
										if self.squares[r][c1]:
											break
										c1 += dc
						case "King":
							moves = ((1, 1), (-1, -1), (1, 0), (-1, 0),
									 (0, 1), (0, -1), (1, -1), (-1, 1))  # all legal moves (relative to cur pos)
							for m in moves:
								dr, dc = m  # delta row, col
								if inBounds(r1 := r + dr) and inBounds(c1 := c + dc) and \
									(self.pos_mtx[r1][c1] != team) and (not inCheckAfter(r, c, r1, c1)):
									addMove(r, c, r1, c1)
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
		self.legal_moves = mtx

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
							print(" p " if cur.team else " P ", end="")
						case "Knight":
							print(" n " if cur.team else " N ", end="")
						case "Bishop":
							print(" b " if cur.team else " B ", end="")
						case "Rook":
							print(" r " if cur.team else " R ", end="")
						case "Queen":
							print(" q " if cur.team else " Q ", end="")
						case "King":
							print(" k " if cur.team else " K ", end="")
						case _:
							pass
				else:
					print(" ∙ ", end="") # ∙□.-
			print("|")
		print("  +------------------------+")

	def printPositionMatrix(self) -> None:
		for r in range(8):
			for c in range(8):
				match self.pos_mtx[r][c]:
					case True:
						print("T ", end="")
					case False:
						print("F ", end="")
					case _:
						print(". ", end ="")
			print()
		print()

	def printControlMatrix(self) -> None:
		print("*********\nCONTROL MATRIX:\n\n")
		for r in range(8):
			print(f"ROW {r}:")
			for c in range(8):
				print(f"({r},{c}) ->", self.control_mtx[r][c])
			print("\n")

	def printLegalMoves(self) -> None:
		print("*********\nLEGAL MOVES:\n\n")
		for r in range(8):
			print(f"ROW {r}:")
			for c in range(8):
				print(f"({r},{c}) ->", self.legal_moves[r][c])
			print("\n")
