from models.pieces import Pawn, Knight, Bishop, Rook, Queen, King

class Board:
	def __init__(self):
		self.initBoard()
		# pos_mtx: binary/null matrix that contains info about what team each piece is on
		# control_mtx: matrix that contains info about what pieces control what squares (both teams)
		# legal_moves: list that contains all legal moves for cur pos (only cur team)
	
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

	def move(self, r: int, c: int, rx: int, cx: int) -> None:
		'''
		move piece @ r,c -> rx,cx
		'''
		move = (r, c, rx, cx)
		p = self.squares[r][c]  # piece @ r,c
		king = p.__class__.__name__ == "King"
		# short castle
		if king and (move in ((0, 4, 0, 6), (7, 4, 7, 6))):
			p.moved = self.squares[r][7].moved = True
			self.squares[r][4], self.squares[r][6] = None, p
			self.squares[r][7], self.squares[r][5] = None, self.squares[r][7]
		# long castle
		elif king and (move in ((0, 4, 0, 2), (7, 4, 7, 2))):
			p.moved = self.squares[r][0].moved = True
			self.squares[r][4], self.squares[r][2] = None, p
			self.squares[r][0], self.squares[r][3] = None, self.squares[r][0]
		# normal move
		else:
			self.squares[r][c], self.squares[rx][cx] = None, p
			if hasattr(p, "moved"):
				p.moved = True
		# update king pos
		if king:
			if p.team:
				self.white_king_pos = (rx, cx)
			else:
				self.black_king_pos = (rx, cx)
	
	def undo(self, r: int, c: int, rx: int, cx: int, p1: object, p2: object, p1_moved: bool) -> None:
		'''
		undo given move

		set piece @ r,c to p1, set piece @ rx,cx to p2, revert p1.moved
		'''
		move = (r, c, rx, cx)
		king = p1.__class__.__name__ == "King"
		# short castle
		if king and (move in ((0, 4, 0, 6), (7, 4, 7, 6))):
			self.squares[r][4], self.squares[r][7] = self.squares[r][6], self.squares[r][5]
			self.squares[r][5] = self.squares[r][6] = None
			self.squares[r][4].moved = self.squares[r][7].moved = False
		# long castle
		elif king and (move in ((0, 4, 0, 2), (7, 4, 7, 2))):
			self.squares[r][4], self.squares[r][0] = self.squares[r][2], self.squares[r][3]
			self.squares[r][3] = self.squares[r][2] = None
			self.squares[r][4].moved = self.squares[r][0].moved = False
		# normal move
		else:
			self.squares[r][c], self.squares[rx][cx] = p1, p2
			if hasattr(p1, "moved"):
				p1.moved = p1_moved
		# revert king pos
		if king:
			if p1.team:
				self.white_king_pos = (r, c)
			else:
				self.black_king_pos = (r, c)

	def makeHumanMove(self, r: int, c: int, rx: int, cx: int) -> None:
		'''
		precondition: move is legal
		'''

		def promote() -> str:
			# promote pawn if on last rank
			inp = None
			while inp not in ("Knight", "Bishop", "Rook", "Queen"):
				inp = input("promote pawn to ... (\"Knight\", \"Bishop\", \"Rook\", \"Queen\")\n").strip()
			return inp
		
		p1, p2 = self.squares[r][c], self.squares[rx][cx]
		# update board state
		self.move(r, c, rx, cx)
		self.updateControlMatrix(r, c, rx, cx, p1, p2)
		self.generatePositionMatrix()
		# promote
		if ((cur := self.squares[rx][cx]).__class__.__name__ == "Pawn") and (rx in (0, 7)):
			match promote():
				case "Knight":
					self.squares[rx][cx] = Knight(cur.team)
				case "Bishop":
					self.squares[rx][cx] = Bishop(cur.team)
				case "Rook":
					self.squares[rx][cx] = Rook(cur.team)
					self.squares.moved = True
				case "Queen":
					self.squares[rx][cx] = Queen(cur.team)
				case _:
					pass
			self.generateControlMatrix()

	def makeBotMove(self, r: int, c: int, rx: int, cx: int) -> None:
		p1, p2 = self.squares[r][c], self.squares[rx][cx]
		# update board state
		self.move(r, c, rx, cx)
		self.updateControlMatrix(r, c, rx, cx, p1, p2)
		self.generatePositionMatrix()
		# auto promote to queen
		if ((cur := self.squares[rx][cx]).__class__.__name__ == "Pawn") and (rx in (0, 7)):
			self.squares[rx][cx] = Queen(cur.team)
			self.generateControlMatrix()

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
	
	def stalemate(self, team: bool, move_count: int) -> bool:
		'''
		if the given team is stalemated
		'''
		
		def noLegalMoves() -> bool:
			return not self.legal_moves

		return (move_count == 200) or ((not self.check(team)) and noLegalMoves())
	
	def checkmate(self, team: bool) -> bool:
		'''
		if the given team is checkmated
		'''

		def noLegalMoves() -> bool:
			return not self.legal_moves

		return self.check(team) and noLegalMoves()
	
	def generatePositionMatrix(self) -> None:
		'''
		generate binary/null matrix that contains info about what team each piece is on
		'''
		mtx = [[None for _ in range(8)] for _ in range(8)]
		for r in range(8):
			for c in range(8):
				mtx[r][c] = cur.team if (cur := self.squares[r][c]) else None
		self.pos_mtx = mtx

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
				if cur := self.squares[r][c]:
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

	def updateControlMatrix(self, r: int, c: int, rx: int, cx: int, p1: object, p2: object) -> None:
		'''
		update the control matrix for all relevant pieces given the move p1 @ r,c -> p2 @ rx,cx
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
						r1, c1 = r + dr, c + dc
						while inBounds(r1) and inBounds(c1):
							removeControl(r, c, r1, c1)
							# piece here, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
							c1 += dc
				case "Queen":
					# diagonal
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
					# straight
					dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
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
				case "King":
					moves = ((1, 1), (-1, -1), (1, 0), (-1, 0),
							 (0, 1), (0, -1), (1, -1), (-1, 1))  # all legal moves (relative to cur pos)
					for m in moves:
						dr, dc = m  # delta row, col
						if inBounds(r1 := r + dr) and inBounds(c1 := c + dc):
							removeControl(r, c, r1, c1)
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
						r1, c1 = r + dr, c + dc
						while inBounds(r1) and inBounds(c1):
							addControl(r, c, r1, c1)
							# piece here, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
							c1 += dc
				case "Queen":
					# diagonal
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
					# straight
					dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
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
				case "King":
					moves = ((1, 1), (-1, -1), (1, 0), (-1, 0),
							 (0, 1), (0, -1), (1, -1), (-1, 1))  # all legal moves (relative to cur pos)
					for m in moves:
						dr, dc = m  # delta row, col
						if inBounds(r1 := r + dr) and inBounds(c1 := c + dc):
							addControl(r, c, r1, c1)
				case _:
					pass
		
		'''
		1) pretend p2 @ rx,cx, remove its control (so not in the way of p1-targeting pieces control)
		2) pretend p1 @ r,c, remove its control
		3) add all pieces targeting r and rc to stack, also remove their control
		4) add p1 control to rx, cx
		5) add back control for all affected pieces
		'''
		pcs = []  # list of affected pieces
		# remove p2's control from rx,cx
		self.squares[rx][cx] = p2
		removeAllControl(rx, cx)
		self.squares[rx][cx] = None
		# remove p1's control from r,c
		self.squares[r][c] = p1
		removeAllControl(r, c)
		self.squares[r][c] = None
		# remove control from all pieces controlling either r,c or rx,cx
		for p in tuple(self.control_mtx[r][c]):
			pr, pc = p
			removeAllControl(pr, pc)
			pcs.append(p)
		for p in tuple(self.control_mtx[rx][cx]):
			pr, pc = p
			removeAllControl(pr, pc)
			pcs.append(p)
		# add control back to all affected pieces
		# put p1 back on rx,cx
		self.squares[rx][cx] = p1
		addAllControl(rx, cx)
		for p in pcs:
			pr, pc = p
			addAllControl(pr, pc)

	def revertControlMatrix(self, r: int, c: int, rx: int, cx: int, p1: object, p2: object) -> None:
		'''
		revert the control matrix to before the move p1 @ r,c -> p2 @ rx,cx
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
						r1, c1 = r + dr, c + dc
						while inBounds(r1) and inBounds(c1):
							removeControl(r, c, r1, c1)
							# piece here, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
							c1 += dc
				case "Queen":
					# diagonal
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
					# straight
					dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
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
				case "King":
					moves = ((1, 1), (-1, -1), (1, 0), (-1, 0),
							 (0, 1), (0, -1), (1, -1), (-1, 1))  # all legal moves (relative to cur pos)
					for m in moves:
						dr, dc = m  # delta row, col
						if inBounds(r1 := r + dr) and inBounds(c1 := c + dc):
							removeControl(r, c, r1, c1)
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
						r1, c1 = r + dr, c + dc
						while inBounds(r1) and inBounds(c1):
							addControl(r, c, r1, c1)
							# piece here, stop
							if self.squares[r1][c1]:
								break
							r1 += dr
							c1 += dc
				case "Queen":
					# diagonal
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
					# straight
					dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))  # all directions (relative)
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
				case "King":
					moves = ((1, 1), (-1, -1), (1, 0), (-1, 0),
							 (0, 1), (0, -1), (1, -1), (-1, 1))  # all legal moves (relative to cur pos)
					for m in moves:
						dr, dc = m  # delta row, col
						if inBounds(r1 := r + dr) and inBounds(c1 := c + dc):
							addControl(r, c, r1, c1)
				case _:
					pass

		'''
		(just after undo move, so p1 is @r,c and p2 @ rx,cx)
		1) remove p2, pretend p1 @ rx,cx, remove control
		2) remove control from all targeting r,c and rx,cx
		3) add control back to r,c (p1 already there)
		4) add control back to pcs
		'''	
		pcs = []  # list of affected pieces
		# remove p2 from r,c
		self.squares[r][c] = None
		# remove p1's control from rx,cx
		self.squares[rx][cx] = p1
		removeAllControl(rx, cx)
		self.squares[rx][cx] = None
		# remove control from all pieces targeting r,c or rx,cx
		for p in tuple(self.control_mtx[r][c]):
			pr, pc = p
			removeAllControl(pr, pc)
			pcs.append(p)
		for p in tuple(self.control_mtx[rx][cx]):
			pr, pc = p
			removeAllControl(pr, pc)
			pcs.append(p)
		# add control back to all affected pieces
		# put p1, p2 back
		self.squares[r][c] = p1
		self.squares[rx][cx] = p2
		addAllControl(r, c)
		addAllControl(rx, cx)
		for p in pcs:
			pr, pc = p
			addAllControl(pr, pc)

	def generateLegalMoves(self, team: bool) -> None:
		'''
		generate matrix that contains all legal moves for given team with cur pos
		'''

		def inBounds(x: int) -> bool:
			return x in range(8)

		def addMove(r: int, c: int, rx: int, cx: int) -> None:
			# if (rx, cx) no t in mtx[r][c]:
			legal.append((r, c, rx, cx))

		def inCheckAfter(r: int, c: int, rx: int, cx: int) -> bool:
			# store relevant info before trying move
			p1, p2 = self.squares[r][c], self.squares[rx][cx]
			p1_moved = p1.moved if hasattr(p1, "moved") else None
			# try move
			self.move(r, c, rx, cx)
			self.updateControlMatrix(r, c, rx, cx, p1, p2)
			self.generatePositionMatrix()
			check = self.check(team)  # in check after move?
			# undo move
			self.undo(r, c, rx, cx, p1, p2, p1_moved)
			self.revertControlMatrix(r, c, rx, cx, p1, p2)
			self.generatePositionMatrix()
			return check

		legal = []
		for r in range(8):
			for c in range(8):
				if (cur := self.squares[r][c]) and (cur.team == team):
					match cur.__class__.__name__:
						case "Pawn":
							dr = -1 if cur.team else 1  # delta row
							if inBounds(r1 := r + dr):
								# push 1
								if (not self.squares[r1][c]) and (not inCheckAfter(r, c, r1, c)):
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
									(self.pos_mtx[r1][c1] != team) and (not inCheckAfter(r, c, r1, c1)):
									addMove(r, c, r1, c1)
						case "Bishop":
							dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all directions (relative)
							for d in dirs:
								dr, dc = d  # delta row, col
								r1, c1 = r + dr, c + dc
								while inBounds(r1) and inBounds(c1) and (self.pos_mtx[r1][c1] != team) \
									and (not inCheckAfter(r, c, r1, c1)):
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
								r1, c1 = r + dr, c + dc
								while inBounds(r1) and inBounds(c1) and (self.pos_mtx[r1][c1] != team) \
									and (not inCheckAfter(r, c, r1, c1)):
									addMove(r, c, r1, c1)
									# piece here, stop
									if self.squares[r1][c1]:
										break
									r1 += dr
									c1 += dc
						case "Queen":
							# diagonals
							dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # all directions (relative)
							for d in dirs:
								dr, dc = d  # delta row, col
								r1, c1 = r + dr, c + dc
								while inBounds(r1) and inBounds(c1) and (self.pos_mtx[r1][c1] != team) \
									and (not inCheckAfter(r, c, r1, c1)):
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
								r1, c1 = r + dr, c + dc
								while inBounds(r1) and inBounds(c1) and (self.pos_mtx[r1][c1] != team) \
									and (not inCheckAfter(r, c, r1, c1)):
									addMove(r, c, r1, c1)
									# piece here, stop
									if self.squares[r1][c1]:
										break
									r1 += dr
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
		print("*********\nPOSITION MATRIX:\n\n")
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
			print(f"row {r}: ", end="")
			for c in range(8):
				print(self.control_mtx[r][c], end=" _ ")
			print("\n")

	def printLegalMoves(self) -> None:
		print("*********\nLEGAL MOVES:\n\n")
		print(self.legal_moves)
