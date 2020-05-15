from Checkers.Piece import Piece as piece
from Checkers.Enums import Team

# This class is the data representation of a space on the board. It does nothing but keep track
# of any pieces that are occupying the space it represents.

class Space:

    def __init__(self):
        self._occupied_by = piece("empty", "empty")

    #----CLASS ATTRIBUTE METHODS----#
    def __eq__(self, other):
        return self._occupied_by == other.get_occupier()

    def __repr__(self):
        if self._occupied_by.get_team() == Team.EMPTY:
            return " "
        elif self._occupied_by.get_team() == Team.BLACK:
            return "B"
        elif self._occupied_by.get_team() ==Team.WHITE:
            return "W"

    #----GETTERS AND SETTERS----#
    def update_occupier(self, team, rank):
        self._occupied_by = piece(team, rank)

    def get_occupier(self):
        return self._occupied_by