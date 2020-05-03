import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
from Checkers.Game import Game
import random as rand
from Checkers.Move import Move
from gym_checkers.envs.action_value_pair import Action_Value_Pair
from copy import deepcopy
import random as rand

class CheckersEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    # Ve = (A2 − A1) + (B2 − B1) + (C1 − C2)
    # Ai = squared sum distance to other side for player i
    # Bi = squared sum distance to centre for all pieces of player i
    # Ci = the sum of maximum vertical advanced for all pieces e.g lower score for pieces near start of board
    # w1, w2, w3, all weights calculated by evaluation func

    #start state, available moves, all same reward, randomly select move, move into state, use policy above to adjust reward,
    #keep track of moves made, further update value of moves if we win/lose, game starts again with a bit new knowledge

    #predictive search of best moves for the state, e.g minmax on the best moves we found in the previous game

    #learning rate, after x games we can reduce the swing of the updates to smaller increments
    

    def __init__(self):

        self.state_action_value_pairs = []
        self.epsilon_greedy_value = 0.1  # 0.1 = 10% of the time pick a random action, 90% time greedy
        self.learning_rate = 1 #1 = harsh punishments/big rewards. 0.1 = small punishments and small rewards
        self.player_agent = None
        self.current_state = None
        self.action_value_pairs = []
        self.games_played = 0

        print("Gym init")

    def step(self, action):

        action.makemove(self.current_state)
        print("Gym step")

    def reset(self):
        print("Gym reset")

    def render(self, mode='human', close=False):
        self.current_state.printboard()
        print("Gym render")

    def calculate_best_move(self):

        #TODO change this to evaluate if current_state == anything in self.state_action_value_pairs
        #TODO if not found, pick random move, then add move + state + value after moving to self.state_action_value_pairs
        if self.games_played == 0:
            action = rand.choice(self.action_value_pairs)
            return action.get_action()
        else:
            #TODO
            return rand.choice(self.action_value_pairs).geta_action()


    def value_from_policy(self, state):
        #calculate state value from policy
        pass

    def update_action_value_pairs(self):

        leftward = [-1, -1]
        rightward = [1, -1]

        for piece in self.player_agent.get_current_moveable_pieces():
            new_leftward_position = [x + y for x, y in zip(piece, leftward)]  # new leftward movement position
            self.append_action_value_pair(piece, new_leftward_position)
            new_rightward_position = [x + y for x, y in zip(piece, rightward)]  # new rightward movement position
            self.append_action_value_pair(piece, new_rightward_position)

    def evaluate_best_move(self):
        pass

    def print_action_value_pairs(self):
        print(self.action_value_pairs)

    def set_player(self, player):
        self.player_agent = player

    def set_current_state(self, board):
        self.current_state = board

    def init_env_vars(self, board, player):
        self.set_current_state(board)
        self.set_player(player)
        self.update_action_value_pairs()

    def get_action_value_pairs(self):
        return self.action_value_pairs

    def append_action_value_pair(self, old_position, new_position):
        if new_position[0] > 0 and new_position[1] > 0:
            self.action_value_pairs.append(Action_Value_Pair(Move(old_position, new_position, self.player_agent, 1), 1))
        else:
            return
