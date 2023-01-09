import models
import cProfile

'''

before game:
- options:
	- another person or ai
		- ai: depth
		- ai: move first?
	
- explain move format

'''

def main1():
	model = models.Model(1)
	model.board.squares[6][4] = models.pieces.Queen(False)
	model.board.generateControlMatrix()
	model.board.generatePositionMatrix()
	model.board.printBoard()
	print(model.board.check(True))

def playBot() -> None:
	model = models.Model(2)
	team = True
	last_move = None  # other team's last move
	for i in range(6):
		# generate matrices
		model.board.generateControlMatrix()	
		model.board.generatePositionMatrix()
		model.board.generateLegalMoves(team)
		# print(model.board.legal_moves)
		# print eval
		print(f"\neval: {model.engine.evaluate(model.board)}, pos = {model.engine.positionEvaluate(model.board)}, mat = {model.engine.materialEvaluate(model.board)}")
		# display board
		print()
		model.board.printBoard()
		print()
		# not first move
		if last_move:
			print("{team}: {last_move}".format(team = ("black" if team else "white"), last_move = last_move))
		# stalemate
		if model.board.checkStale(team):
			print("stalemate. it's a draw.")
			return
		# checkmate
		if model.board.checkMate(team):
			print("checkmate. {team} wins!".format(team = ("black" if team else "white")))
			return
		# check
		if model.board.checkCheck(team):
			if model.board.checkMate(team):
				print("checkmate. {team} wins!".format(team = ("black" if team else "white")))
			print("you're in check.\n")
		inp = ""  # user input
		# must be valid + legal move
		while not (model.board.validMove(inp, team) and model.board.legalMove(inp)) :
			inp = input("{team}'s move?\n".format(team = ("white" if team else "black").strip()))
		# valid move given, move that piece
		model.board.movePiece(inp)
	
		model.board.generateControlMatrix()
		model.board.generatePositionMatrix()
		model.board.generateLegalMoves(team)
		print(f"\neval: {model.engine.evaluate(model.board)}, pos = {model.engine.positionEvaluate(model.board)}, mat = {model.engine.materialEvaluate(model.board)}")
		print(); model.board.printBoard(); print()
		model.bot.bot_move(model.board, not team)
		# update last move
		last_move = inp
		# next team's turn
		team = not team

def main() -> None:
	model = models.Model(1)
	team = True  # white moves first
	last_move = None  # other team's last move
	# game loop
	while True:
		print("\n\n\n\n\n\n\n\n\n\n\n")
		model.board.generateLegalMoves(team)
		model.board.printPositionMatrix()
		model.board.printControlMatrix()
		model.board.printLegalMoves()
		# print eval
		print(f"eval: {model.engine.evaluate(model.board)}")
		# display board
		print()
		model.board.printBoard()
		print()
		# not first move
		if last_move:
			print("{team}: {last_move}".format(team = ("black" if team else "white"), last_move = last_move))
		# stalemate
		if model.board.stalemate(team, model.move_cnt):
			print("stalemate. it's a draw.")
			return
		# checkmate
		if model.board.checkmate(team):
			print("checkmate. {team} wins!".format(team = ("black" if team else "white")))
			return
		# check
		if model.board.check(team):
			print("you're in check.\n")
		inp = ""  # user input
		# must be valid + legal move
		while not (model.validMove(inp) and model.legalMove(inp)) :
			inp = tuple(int(c) for c in input("{team}'s move?\n".format(team = ("white" if team else "black").strip())) if c.isdigit())
		# valid move given, move that piece
		r, c, rx, cx = inp
		model.board.humanMove(r, c, rx, cx)
		# update move count
		model.move_cnt += 1
		# update last move
		last_move = inp
		# next team's turn
		team = not team

if __name__ == "__main__":
	playBot()