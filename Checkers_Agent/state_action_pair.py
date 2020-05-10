class State_Action_Pair:

    def __init__(self, state, action_value_pair):
        self.state = state
        self.action_value_pair = action_value_pair

    def get_state(self):
        return self.state

    def get_action(self):
        return self.action_value_pair.get_action()

    def get_action_pair(self):
        return self.action_value_pair

    def compare_to_current_board(self, current_board):

        if self.state == current_board:
            return True
        else:
            return False

    def __str__(self):

        return "State :" + self.state + "Value : " + str(self.action_value_pair.get_value())

    def __repr__(self):

        return "State :" + self.state + "Value : " + str(self.action_value_pair.get_value())

    def __eq__(self, other):
        return self.state == other
