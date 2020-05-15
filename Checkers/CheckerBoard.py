from Checkers.Space import Space as space


# This class is the data structure representation of a checkerboard.
# The methods contained within this class are used to initialise a board, fill it with pieces, and render them.

class CheckerBoard:
    _board = [[]]

    def __init__(self, x, y):
        self._board = [[space() for i in range(x)] for j in range(y)]

        self._height = y
        self._width = x

    #----CLASS ATTRIBUTE METHODS----#
    def __getitem__(self, key):
        # Tuple unpack, key = [x, y]
        x, y = key

        return self._board[x][y]

    def __repr__(self):
        return str(self._board)

    #----BOARD METHODS----#
    def printboard(self):
        for row in zip(*self._board):
            print("".join(str(row)))

    def setupdefaultboard(self):
        # Check if normal 8x8 board, assumes 8x8 anyway, just checking for debug purposes.
        if self._width == 8:
            for i in range(8):
                if i % 2 == 0:
                    # Set even space white checkers
                    self._board[i][1].update_occupier("white", "basic")

                    # Set even space black checkers
                    self._board[i][5].update_occupier("black", "basic")
                    self._board[i][7].update_occupier("black", "basic")


                else:
                    # Set odd space white checkers
                    self._board[i][0].update_occupier("white", "basic")
                    self._board[i][2].update_occupier("white", "basic")

                    # Set odd space black checkers
                    self._board[i][6].update_occupier("black", "basic")

    #----SETTERS AND GETTERS----#
    def get_x(self):
        return self._width

    def get_y(self):
        return self._height

    def get_board(self):
        return self._board
