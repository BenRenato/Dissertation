class State_Action_Pair:

    def __init__(self, state, action, value=0):
        self.state = state
        self.action_value = action
        self.value = value

    def get_state(self):
        return self.state

    def get_action(self):
        return self.action_value.get_action()

    def __str__(self):
        pass

    def __repr__(self):
        pass
