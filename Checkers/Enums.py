from enum import Enum


class Team(Enum):
    BLACK = "black"

    WHITE = "white"

    EMPTY = "empty"

class PieceRank(Enum):
    BASIC = "basic"

    KING = "king"

    EMPTY = "empty"

class Direction(Enum):
    UP = "up"

    DOWN = "down"

    LEFT = "left"

    RIGHT = "right"

class Player_Types(Enum):
    HUMAN = "human"

    AI = "ai"

    RANDOM = "random"

    HEURISTIC = "heuristic"

class Outcome(Enum):
    WIN = 1

    TIE = 0

    LOSE = -1

class Game_Type(Enum):
    PvP = 1

    RvR = 2

    RvH = 3

    HvH = 4

    RvAI = 5

    AIvAI = 6

    HvAI = 7
