import models
import copy

'''

before game:
- options:
	- another person or ai
		- ai: depth
		- ai: move first?
	
- explain move format

'''

def main() -> None:
	model = models.Model(2)
	team = True
	model.board.generateControlMatrix()
	model.board.generatePositionMatrix()
	model.board.generateLegalMoves(team)
	print(f"\neval: {model.engine.simpleEvaluate(model.board)}")
	print(); model.board.printBoard(); print()

	model.bot.bot_move(model.board, team)
	
	model.board.generateControlMatrix()
	model.board.generatePositionMatrix()
	model.board.generateLegalMoves(team)
	print(f"eval: {model.engine.simpleEvaluate(model.board)}")
	print(); model.board.printBoard(); print()


	return
	model = models.Model()
	engine = models.Engine()
	team = True  # white moves first
	last_move = None  # other team's last move
	# game loop
	while True:
		# generate matrices
		model.board.generateControlMatrix()
		model.board.generatePositionMatrix()
		model.board.generateLegalMoves(team)
		# print(model.board.legal_moves)
		# print eval
		print(f"eval: {engine.simpleEvaluate(model.board)}")
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
		# update last move
		last_move = inp
		# next team's turn
		team = not team

if __name__ == "__main__":
	main()