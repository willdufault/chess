"""
********************************************************
Please read the README for instructions on how to play.

https://github.com/willdufault/chess/blob/main/README.md
********************************************************
"""

from textwrap import dedent
import models
# import cProfile

def main() -> None:
    """
    Prompt the player to select a game mode.
    """
    intro_message = dedent('''
        Thanks for playing Will Dufault's and Matthes Faria's Chess with AI Python \
        project! Please read the README for instructions on how to play.

        (https://github.com/willdufault/chess/blob/main/README.md)\n'''.replace(' ' * 8, ''))
    print(intro_message)

    # Player selects a game mode.
    mode = ''
    
    while mode not in ('1', '2'):
        prompt = 'Would you like to play against another player (1) or play against our AI (2)?\n'
        mode = input(prompt).strip()

    if mode == '1':
        playHuman()

    elif mode == '2':
        playBot()
    
    else:
        print('Error reading input. Please run the program again.\n')

def playHuman() -> None:
    """
    Play a game of chess against another real player.
    """
    model = models.Model(0)
    team = True
    prev_move = None

    while True:
        model.board.generateLegalMoves(team)

        print(f'\nEvaluation: {model.engine.evaluate(model.board)}\n')
        model.board.printBoard(); print()

        if prev_move is not None:
            print(f'{"Black" if team else "White"}: {prev_move}')

        if model.board.stalemate(team, model.move_count):
            print("Stalemate. It's a draw.\n")
            break
        
        if model.board.checkmate(team):
            print(f'Checkmate. {"Black" if team else "White"} wins!\n')
            break

        if model.board.check(team):
            print('You\'re in check.\n')
        
        # Player inputs their next move.
        move = ''
        
        # Move is either incorrectly formatted or illegal.
        while not model.validMove(move) or not model.legalMove(move):
            prompt = f'{"White" if team else "Black"}\'s move?\n'
            move = tuple(int(char) for char in input(prompt) if char.isdigit())

        prev_move = move
        r, c, rx, cx, = move

        model.board.makeHumanMove(r, c, rx, cx)
        model.updateMoveCount()
        team = not team

def playBot() -> None:
    """
    Play a game of chess against the AI.
    """
    # Player selects a depth for the AI.
    # Note: You can play with a depth > 3 but it will be extremely slow.
    MAX_DEPTH = 3
    depth =''

    while depth not in map(str, range(MAX_DEPTH + 1)):
        prompt = dedent(f'''
            Please specify a depth for the AI in the range [0, {MAX_DEPTH}]. (This \
            is how many moves ahead the bot will look. Depth 3 takes ~30 seconds.)\n'''
            .replace(' ' * 12, ''))
        depth = input(prompt).strip()

    model = models.Model(int(depth))
    team = ''

    while team not in ('1', '2'):
        prompt = '\nDo you want to play as white (1) or black (2)?\n'
        team = input(prompt).strip()
    
    team = team == '1'
    prev_move = None

    # Bot moves first if the user chose black.
    if not team:
        model.board.generateLegalMoves(not team)

        print(f'\nEvaluation: {model.engine.evaluate(model.board)}\n')
        model.board.printBoard(); print()
        
        print("Bot thinking...")

        prev_move = model.bot.calculateBestMove(model.board, not team, model.move_count)
        model.updateMoveCount()

    while True:
        # Player's turn to make a move.
        model.board.generateLegalMoves(team)

        print(f'\nEvaluation: {model.engine.evaluate(model.board)}\n')
        model.board.printBoard(); print()

        if prev_move is not None:
            print(f'{"Black" if team else "White"}: {prev_move}')

        if model.board.stalemate(team, model.move_count):
            print('Stalemate. It\'s a draw.\n')
            break

        if model.board.checkmate(team):
            print(f'Checkmate. {"Black" if team else "White"} wins!\n')
            break

        if model.board.check(team):
            print('You\'re in check.\n')
            
        # Player inputs their next move.
        move = ''

        # Move is either incorrectly formatted or illegal.
        while not model.validMove(move) or not model.legalMove(move):
            prompt = f'{"White" if team else "Black"}\'s move?\n'
            move = tuple(int(char) for char in input(prompt) if char.isdigit())

        prev_move = move
        r, c, rx, cx, = move

        model.board.makeHumanMove(r, c, rx, cx)
        
        # Bot's turn to make a move.
        team = not team

        model.board.generateLegalMoves(team)
        
        print(f'\nEvaluation: {model.engine.evaluate(model.board)}\n')
        model.board.printBoard(); print()

        if prev_move is not None:
            print(f'{"Black" if team else "White"}: {prev_move}')

        if model.board.stalemate(team, model.move_count):
            print('Stalemate. It\'s a draw.\n')
            break

        if model.board.checkmate(team):
            print(f'Checkmate. {"Black" if team else "White"} wins!\n')
            break

        if model.board.check(team):
            print('You\'re in check.\n')

        print("Bot thinking...")

        prev_move = model.bot.calculateBestMove(model.board, team, model.move_count)
        model.updateMoveCount()
        
        # Switch back to player's team.
        team = not team
        
if __name__ == "__main__":
    main()