from Checkers.Piece import Piece as piece


class Space:

    def __init__(self):
        self._OccupiedBy = piece("empty", "empty")

    def updateoccupier(self, team, rank):
        self._OccupiedBy = piece(team, rank)

    def getoccupier(self):
        return self._OccupiedBy

    def __eq__(self, other):
        return self._OccupiedBy == other

    def __repr__(self):
        if self._OccupiedBy.team == self._OccupiedBy.team.EMPTY:
            return " "
        elif self._OccupiedBy.team == self._OccupiedBy.team.BLACK:
            return "B"
        elif self._OccupiedBy.team == self._OccupiedBy.team.WHITE:
            return "W"
