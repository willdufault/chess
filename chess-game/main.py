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
	team = True  # white moves first
	last_move = None
	# game loop
	while True:
		model.generateControlMatrix()
		model.generatePositionMatrix()
		model.generateLegalMoves(team)
		print()
		model.printBoard()
		print()
		if last_move:
			print("{team}: {last_move}".format(team = ("black" if team else "white"), last_move = last_move))
		if model.checkStale(team):
			print("stalemate. it's a draw.")
			return
		if model.checkCheck(team):
			if model.checkMate(team):
				print("checkmate. {team} wins!".format(team = ("black" if team else "white")))
			print("you're in check.\n")
		inp = ""
		while not (model.validMove(inp, team) and model.legalMove(inp)) :
			inp = input("{team}'s move?\n".format(team = ("white" if team else "black").strip()))
		model.movePiece(inp)
		last_move = inp
		team = not team

if __name__ == "__main__":
	main()