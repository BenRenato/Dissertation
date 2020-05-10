from Checkers.Space import Space as space


class CheckerBoard:
    _board = [[]]

    def __init__(self, x, y):
        # TODO explain this list comprehension optimisation
        self._board = [[space() for i in range(x)] for j in range(y)]
        self.height = y
        self.width = x

    def __getitem__(self, key):
        # Tuple unpack, key = [x, y]
        x, y = key
        return self._board[x][y]

    def __eq__(self, other):
        return self._board == other

    def compare_board_with_state_action_pair(self, state_action_pair):
        if self._board == state_action_pair.get_state():
            return True
        else:
            return False

    def printboard(self):
        for row in zip(*self._board):
            print("".join(str(row)))

    def setupdefaultboard(self):
        # Check if normal 8x8 board, assumes 8x8 anyway, just checking for debug purposes.
        if self.width == 8:
            for i in range(8):
                if i % 2 == 0:
                    # Set even space white checkers
                    self._board[i][1].updateoccupier("white", "basic")

                    # Set even space black checkers
                    self._board[i][5].updateoccupier("black", "basic")
                    self._board[i][7].updateoccupier("black", "basic")


                else:
                    # Set odd space white checkers
                    self._board[i][0].updateoccupier("white", "basic")
                    self._board[i][2].updateoccupier("white", "basic")

                    # Set odd space black checkers
                    self._board[i][6].updateoccupier("black", "basic")

    def get_x(self):
        return self.width

    def get_y(self):
        return self.height