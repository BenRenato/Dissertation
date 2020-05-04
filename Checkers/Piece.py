from Checkers.Enums import *


class Piece:

    def __init__(self, team, rank):
        self.team = Team(team)
        self.rank = PieceRank(rank)

    def __str__(self):
        return str(self.team)

    def __repr__(self):
        return self.team

    def __eq__(self, other):
        return self.team == other.team
