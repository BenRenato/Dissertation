from Checkers.Enums import *

# This class is the data representation of a piece on a checkerboard.
# No logic happens here. Just setters and getters.

class Piece:

    def __init__(self, team, rank):
        self._team = Team(team)
        self._rank = PieceRank(rank)

    # ----CLASS ATTRIBUTE METHODS----#
    def __str__(self):
        return str(self._team)

    def __repr__(self):
        return self._team

    def __eq__(self, other):
        return self._team == other.get_team()

    #----SETTERS AND GETTERS----#
    def get_team(self):
        return self._team

    def get_rank(self):
        return self._rank

    def set_rank(self, rank):
        self._rank = rank

    def set_team(self, team):
        self._team = team


