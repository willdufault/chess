import models

'''

before game:
- options:
	- another person or ai
		- ai: depth
		- ai: move first?
	
- explain move format

'''

def main() -> None:
	model = models.Model()
	engine = models.Engine()
	team = True  # white moves first
	last_move = None  # other team's last move
	# game loop
	while True:
		# generate matrices
		model.generateControlMatrix()
		model.generatePositionMatrix()
		model.generateLegalMoves(team)
		print(model.legal_moves)
		# print eval
		print(f"eval: {engine.simpleEvaluate(model.board)}")
		# display board
		print()
		model.printBoard()
		print()
		# not first move
		if last_move:
			print("{team}: {last_move}".format(team = ("black" if team else "white"), last_move = last_move))
		# stalemate
		if model.checkStale(team):
			print("stalemate. it's a draw.")
			return
		# checkmate
		if model.checkMate(team):
			print("checkmate. {team} wins!".format(team = ("black" if team else "white")))
			return
		# check
		if model.checkCheck(team):
			if model.checkMate(team):
				print("checkmate. {team} wins!".format(team = ("black" if team else "white")))
			print("you're in check.\n")
		inp = ""  # user input
		# must be valid + legal move
		while not (model.validMove(inp, team) and model.legalMove(inp)) :
			inp = input("{team}'s move?\n".format(team = ("white" if team else "black").strip()))
		# valid move given, move that piece
		model.movePiece(inp)
		# update last move
		last_move = inp
		# next team's turn
		team = not team

if __name__ == "__main__":
	main()