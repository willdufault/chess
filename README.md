# chess

Chess with Artificial Intelligence by Will Dufault and Mattheus Faria.

## How to Play:
- Black is on top (CAPS)
- White is on bottom (lower)
- Moves are of the form rcRC (all ints between 0-7), piece on (r, c) moves to (R, C)
- Short castle is 0406 (white) or 7476 (black)
- Long castle is 0402 (white) or 7472 (black)
- Inputting an illegal move will cause the game to simply re-print the prompt

## The Different Parts:
- The game itself (model.py, board.py)
	- Uses no external libraries, completely custom
- The engine (engine.py)
	- A very simple 0-depth engine that evaluates the current board based on
		- Positional advantage: if pieces are on good squares (see position_scores in models/engine.py)
		- Material advantage: simple calculation, sum of white piece values minus sum of black piece values
		- Space-control adavantage: an evaluation based on how many spaces a piece "controls" multiplied by its piece value 
			- ex: A knight at the start of the game controls 2 spaces, multiplied by its piece value of 3, one knight has a control evaluation of 6
- The AI (bot.py)
	- Uses an optimized version of minimax with alpha-beta pruning and memoization to look ahead and select moves
