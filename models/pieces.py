"""
*******************************************************************************
NOTE: This is poor design. When I have time, I will go back and clean this up
      to inherit from a parent Piece class. I will also add more fields and 
      methods to each child class to reduce repeat code in Board.py.
*******************************************************************************
"""

class Pawn:
    def __init__(self, team: bool):
        self.team = team
        self.value = 1
        self.moved = False # For moving up two tiles.

class Knight:
    def __init__(self, team: bool):
        self.team = team
        self.value = 3

class Bishop:
    def __init__(self, team: bool):
        self.team = team
        self.value = 3

class Rook:
    def __init__(self, team: bool):
        self.team = team
        self.value = 5
        self.moved = False # For castling.

class Queen:
    def __init__(self, team: bool):
        self.team = team
        self.value = 9

class King:
    def __init__(self, team: bool):
        self.team = team
        self.value = 99 # Priceless.
        self.moved = False # For castling.