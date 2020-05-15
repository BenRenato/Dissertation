
# This class is akin to ActionValuePair.py except it represents the link between an action value pair
# and the state that the pair was executed upon. It is used by the Checkers_env agent to easily identify
# past states seen and what move was taken.

class StateActionPair:

    def __init__(self, state, action_value_pair):
        self._state = state

        self._action_value_pair = action_value_pair

    # ----CLASS ATTRIBUTE METHODS----#
    def __str__(self):
        return "State :" + self._state + "Value : " + str(self._action_value_pair.get_value())

    def __repr__(self):
        return "State :" + self._state + "Value : " + str(self._action_value_pair.get_value())

    def __eq__(self, other):
        return self._state == other

    #----GETTERS AND SETTERS----#
    def get_state(self):
        return self._state

    def get_action(self):
        return self._action_value_pair.get_action()

    def get_action_pair(self):
        return self._action_value_pair

    #----CUSTOM COMPARE METHOD----#
    def compare_to_current_board(self, current_board):
        if self._state == current_board:
            return True

        else:
            return False


