import models
import cProfile  # profiler used to measure bot.bestMove

'''
******************************************

please read the readme.md for instructions

******************************************
'''
def main() -> None:
	print("\nthanks for playing Will Dufault's and Mattheus Faria's python chess with AI!")
	print("please read the README for instructions on how to play. (github.com/wduf/chess -> README.md)\n")
	mode = ""
	while mode not in ("1", "2"):
		msg = "would you like to play against another player (1) or play against our AI (2)?\n"
		mode = input(msg).strip()
	mode = int(mode)
	if mode == 1:
		playHuman()
	elif mode == 2:
		playBot()
	else:
		print("error reading input. please run the program again.\n")

def playHuman() -> None:
	model = models.Model(0)
	team = True
	last_move = None
	while True:
		model.board.generateLegalMoves(team)
		print("\neval:", model.engine.evaluate(model.board), "\n")
		model.board.printBoard(); print()
		if last_move:
			print("{team}: {last_move}\n".format(team=("black" if team else "white"), last_move=last_move))
		if model.board.stalemate(team, model.move_cnt):
			print("stalemate. it's a draw.\n")
			break
		if model.board.checkmate(team):
			print("checkmate. {team} wins!\n".format(team=("black" if team else "white")))
			break
		if model.board.check(team):
			print("you're in check.\n")
		move = ""
		while not (model.validMove(move) and model.legalMove(move)) :
			msg = "{team}'s move?\n".format(team=("white" if team else "black"))
			move = tuple(int(c) for c in input(msg) if c.isdigit())
		last_move = move
		r, c, rx, cx, = move
		model.board.humanMove(r, c, rx, cx)
		model.updateMoveCount()
		# switch teams
		team = not team

def playBot() -> None:
	depth = ""
	while depth not in ("0", "1", "2", "3"):  # can play with depth > 3, but will be painfully slow (it's python, what can you do)
		msg = "\nplease input a number between 0 and 3 (inclusive).\n(this is how many moves ahead the bot will look, depth 3 takes ~30 seconds)\n"
		depth = input(msg).strip()
	depth = int(depth)
	model = models.Model(depth)
	team = ""
	while team not in ("1", "2"):
		msg = "\ndo you want to play as white (1) or black (2)?\n"
		team = input(msg).strip()
	team = True if (team == "1") else False
	print("team:", team)
	last_move = None
	# user chose black, bot moves first
	if not team:
		model.board.generateLegalMoves(not team)
		print("\neval:", model.engine.evaluate(model.board), "\n")
		model.board.printBoard(); print()
		print("bot thinking...")
		last_move = model.bot.bestMove(model.board, not team, model.move_cnt)
		model.updateMoveCount()
	while True:
		model.board.generateLegalMoves(team)
		print("\neval:", model.engine.evaluate(model.board), "\n")
		model.board.printBoard(); print()
		if last_move:
			print("{team}: {last_move}\n".format(team=("black" if team else "white"), last_move=last_move))
		if model.board.stalemate(team, model.move_cnt):
			print("stalemate. it's a draw.\n")
			break
		if model.board.checkmate(team):
			print("checkmate. {team} wins!\n".format(team=("black" if team else "white")))
			break
		if model.board.check(team):
			print("you're in check.\n")
		move = ""
		while not (model.validMove(move) and model.legalMove(move)) :
			msg = "{team}'s move?\n".format(team=("white" if team else "black"))
			move = tuple(int(c) for c in input(msg) if c.isdigit())
		last_move = move
		r, c, rx, cx, = move
		model.board.humanMove(r, c, rx, cx)
		# switch teams
		team = not team
		model.board.generateLegalMoves(team)
		print("\neval:", model.engine.evaluate(model.board), "\n")
		model.board.printBoard(); print()
		if last_move:
			print("{team}: {last_move}\n".format(team=("black" if team else "white"), last_move=last_move))
		if model.board.stalemate(team, model.move_cnt):
			print("stalemate. it's a draw.\n")
			break
		if model.board.checkmate(team):
			print("checkmate. {team} wins!\n".format(team=("black" if team else "white")))
			break
		if model.board.check(team):
			print("you're in check.\n")
			print("bot thinking...")
		last_move = model.bot.bestMove(model.board, team, model.move_cnt)
		model.updateMoveCount()
		# switch teams
		team = not team
		
if __name__ == "__main__":
	main()