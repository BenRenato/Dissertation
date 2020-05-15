class ActionValuePair:

    def __init__(self, move, value):

        self._move = move
        self._value = value

    def get_action_value_pair(self):
        return self._move, self._value

    def get_value(self):
        return self._value

    def get_action(self):
        return self._move

    def update_value(self, value):
        self._value = value

    def __str__(self):
        return "Move: " + str(self._move) + "Value: " + str(self._value)

    def __repr__(self):
        return "Move: " + str(self._move) + " Value: " + str(self._value) + "\n"