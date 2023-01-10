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

def test():
	model = models.Model(1)
	model.board.generateLegalMoves(True)
	model.board.printControlMatrix()
	model.board.printBoard()
	model.board.humanMove(0, 0, 1, 1)
	model.board.printControlMatrix()
	model.board.printBoard()
	# model.board.printLegalMoves()

def main():
	model = models.Model(1)
	model.board.printControlMatrix()
	model.board.updateControlMatrix(6, 4, 4, 4)
	model.board.printControlMatrix()
	model.board.move(6, 4, 4, 4)
	model.board.generatePositionMatrix()
	model.board.printControlMatrix()
	model.board.updateControlMatrix(0, 6, 2, 5)
	model.board.move(0, 6, 2, 5)
	model.board.generatePositionMatrix()
	model.board.printControlMatrix()
	# model.board.squares[6][4] = models.pieces.Queen(False)
	# model.board.generateControlMatrix()
	# model.board.generatePositionMatrix()
	# model.board.printBoard()
	# print(model.board.check(True))

def playBot() -> None:
	model = models.Model(3)
	team = True
	last_move = None  # other team's last move
	for _ in range(10):
		model.board.generateLegalMoves(team)
		# engine eval
		print(f"\neval: {model.engine.evaluate(model.board)}, pos = {.1 * model.engine.positionEvaluate(model.board)}, mat = {50 * model.engine.materialEvaluate(model.board)}")
		# display board
		print(); model.board.printBoard(); print()
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

		r, c, rx, cx = last_move = inp
		model.board.humanMove(r, c, rx, cx)

		# bot turn
		team = not team
		model.board.generateLegalMoves(team)

		#! need to add stale+checkmate check here
		# break
		print()
		print(f"\neval: {model.engine.evaluate(model.board)}, pos = {0.1 * model.engine.positionEvaluate(model.board)}, mat = {50 * model.engine.materialEvaluate(model.board)}")
		print(); model.board.printBoard(); print()
		print("{team}: {last_move}".format(team = ("black" if team else "white"), last_move = last_move))
		# bot makes best move according to engine
		model.bot.bestMove(model.board, team, model.move_cnt)
		# update last move
		#! need to fix bot last move (make best_move return it)
		last_move = inp
		# human turn
		team = not team
		model.board.generateLegalMoves(team)
		model.board.printPositionMatrix()
		model.board.printControlMatrix()

if __name__ == "__main__":
	# main()
	playBot()
	# cProfile.run("playBot()")
	# test()