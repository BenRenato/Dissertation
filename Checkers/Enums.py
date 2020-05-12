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

class Outcome(Enum):

    WIN = 1
    TIE = 0
    LOSE = -1

class Game_Type(Enum):

    PvP = 1
    RvR = 2
    RvAI = 3
    AIvsAI = 4