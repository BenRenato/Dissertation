from Checkers.Piece import Piece as piece
from Checkers.Enums import Team


class Space:

    def __init__(self):
        self._occupied_by = piece("empty", "empty")

    def updateoccupier(self, team, rank):
        self._occupied_by = piece(team, rank)

    def get_occupier(self):
        return self._occupied_by

    def __eq__(self, other):
        return self._occupied_by == other.get_occupier()

    def __repr__(self):
        if self._occupied_by.get_team() == Team.EMPTY:
            return " "
        elif self._occupied_by.get_team() == Team.BLACK:
            return "B"
        elif self._occupied_by.get_team() ==Team.WHITE:
            return "W"
