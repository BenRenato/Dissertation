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