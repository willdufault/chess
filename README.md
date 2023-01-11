# chess-new

chess with ai by will dufault and mattheus faria

## how to play:
- black is on top (CAPS)
- white is on bottom (lower)
- moves are of the form rcRC (all ints between 0-7), piece on (r, c) moves to (R, C)
- short castle is 0406 (white) or 7476 (black)
- long castle is 0402 (white) or 7472 (black)
- inputting an illegal move will cause the game to simply re-print the prompt

## the different pieces:
- the game itself (model.py, board.py)
	- uses no external libraries, completely custom
- the engine (engine.py)
	- a very simple 0-depth engine that evaluates the current board based on
		- positional advantage: if pieces are on good squares (see position_scores in models/engine.py)
		- material advantage: simple calculation, sum of white piece values minus sum of black piece values
		- space-control adavantage: an evaluation based on how many spaces a piece "controls" multiplied by its piece value 
			- ex: A knight at the start of the game controls 2 spaces, multiplied by its piece value of 3, one knight has a control evaluation of 6
- the AI (bot.py)
	- uses an optimized version of minimax with alpha-beta pruning and memoization to look ahead and select moves
