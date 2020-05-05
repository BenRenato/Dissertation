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

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def __eq__(self, other):
        return self.state == other
