from time import sleep

import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
from Checkers.Game import Game
from Checkers.Enums import Team
from Checkers.Move import Move
from gym_checkers.envs.state_action_pair import State_Action_Pair
from gym_checkers.envs.action_value_pair import Action_Value_Pair
from copy import deepcopy
import random as rand
from math import exp


class CheckersEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    # Ve =  α(A2 − A1) +  α(B2 − B1) +  α(C1 - C2)
    # Ai = squared sum distance to other side for player i
    # Bi = squared sum distance to centre for all pieces of player i
    # Ci = the sum of maximum vertical advanced for all pieces e.g lower score for pieces near start of board
    #  α = learning rate between 0 - 1.0
    # w1, w2, w3, all weights calculated by evaluation func MAYBE

    # start state, available moves, all same reward, randomly select move, move into state, use policy above to adjust reward,
    # keep track of moves made, further update value of moves if we win/lose, game starts again with a bit new knowledge

    # predictive search of best moves for the state, e.g minmax on the best moves we found in the previous game

    # learning rate, after x games we can reduce the swing of the updates to smaller increments

    def __init__(self):

        self.state_action_value_pairs = []
        self.epsilon_greedy_value = 0.1  # 0.1 = 10% of the time pick a random action, 90% time greedy
        self.learning_rate = 1.0  # 1 = harsh punishments/big rewards. 0.1 = small punishments and small rewards
        self.player_agent = None
        self.current_state = None
        self.action_value_pairs = []
        self.games_played = 0

        print("Gym init")

    def step(self, action):

        #TODO SOMETHING WRONG WITH ACTION VALUE PAIR START POSITIONS, THEY ARE RETURNING AS UNSPECIFIED STARTING POSITIONS
        action.makemove(self.current_state)

        print("Gym step")

    def reset(self):
        print("Gym reset")

    def render(self, mode='human', close=False):
        #self.current_state.printboard()
        print("Gym render")

    def calculate_best_move(self):

        possible_action_values = []
        # TODO change this to evaluate if current_state == anything in self.state_action_value_pairs
        # TODO if not found, pick random move, then add move + state + value after moving to self.state_action_value_pairs

        for pair in self.get_action_value_pairs():
            temp_state = deepcopy(self.current_state)
            action_to_evaluate = pair.get_action()
            action_to_evaluate.makemove(temp_state)

            state_value = self.state_value_from_policy(temp_state)

            possible_action_values.append(Action_Value_Pair(action_to_evaluate, state_value))

        if self.games_played == 0 or rand.randint(0, 1) > self.epsilon_greedy_value:
            action = rand.choice(self.action_value_pairs)
            return action.get_action()

        matching_state = next((x for x in self.state_action_value_pairs if self.current_state == x.get_state()), None)

        if matching_state is not None:
            possible_action_values.append(matching_state.get_action_pair())

        best_move = self.evaluate_best_move(possible_action_values)

        self.state_action_value_pairs.append(State_Action_Pair(self.current_state, best_move.get_action()))

        return best_move.get_action()


    #Ignore PyCharm suggesting static method, we don't want to call this without a class instance
    def evaluate_best_move(self, moves):

        best_move_so_far = None

        for move in moves:

            if best_move_so_far is None:
                best_move_so_far = move
            elif move.get_value() > best_move_so_far.get_value():
                best_move_so_far = move

        return best_move_so_far

    # Ve =  α(A2 − A1) +  α(B2 − B1) +  α(C1 - C2) MAYBE(- α(Di))
    # Ai = squared sum distance to other side for player i
    # Bi = squared sum distance to centre for all pieces of player i
    # Ci = counters owned by player
    # Di = "exposed" counters that can be taken after move?

    def state_value_from_policy(self, state):

        # [0] = column
        # [1] = row

        # Ai
        black_sum_distance_to_other_side = 0

        white_sum_distance_to_other_side = 0

        # Bi
        black_sum_of_distance_to_centre = 0

        white_sum_distance_to_centre = 0

        # Ci
        black_counters_on_board = 0

        white_counters_on_board = 0

        # TODO clean up please future Ben
        for i in range(state.get_x()):
            for j in range(state.get_y()):
                if state[i, j].getoccupier().team == Team.BLACK:
                    black_sum_distance_to_other_side += self.calculate_distance_to_other_side(j, Team.BLACK)
                    black_sum_of_distance_to_centre += self.calculate_distance_from_centre(i)
                    black_counters_on_board += 1

                elif state[i, j].getoccupier().team == Team.WHITE:
                    white_sum_distance_to_other_side += self.calculate_distance_to_other_side(j, Team.WHITE)
                    white_sum_distance_to_centre += self.calculate_distance_from_centre(i)
                    white_counters_on_board += 1

        # TODO once verified working and merge into return statement
        state_value = self.calculate_policy_with_current_values(black_sum_distance_to_other_side,
                                                                white_sum_distance_to_other_side
                                                                , black_sum_of_distance_to_centre,
                                                                white_sum_distance_to_centre
                                                                , black_counters_on_board, white_counters_on_board)

        return state_value

    def calculate_policy_with_current_values(self, a1, a2, b1, b2, c1, c2):
        # Ve =  α(A2 − A1) +  α(B2 − B1) +  α(C1 - C2)
        alpha = self.learning_rate

        return alpha * (exp(a2) - exp(a1)) + alpha * (exp(b2) - exp(b1)) + alpha * (c1 - c2)

    def calculate_distance_to_other_side(self, y_position, side):

        if y_position == 0 or y_position == 1:
            if side == Team.BLACK:
                return 1.0
            elif side == Team.WHITE:
                return 0.0
        elif y_position == 2 or y_position == 3:
            if side == Team.BLACK:
                return 1.0
            elif side == Team.WHITE:
                return 1.0
        elif y_position == 4 or y_position == 5:
            if side == Team.BLACK:
                return 0.5
            elif side == Team.WHITE:
                return 0.5
        elif y_position == 6 or y_position == 7:
            if side == Team.BLACK:
                return 0.0
            elif side == Team.WHITE:
                return 1.0

    # Update state_space data based on win/lose
    def post_game_heuristics(self):
        # TODO edit move values based on win/lose, adjust alpha learning rate here too, possibly change epsilon
        pass

    def calculate_distance_from_centre(self, x_position):

        # find difference between index and centre
        # if difference is 0, it's at centre, then take difference of that, 4 = high value at center

        if x_position == 0 or x_position == 7:
            return -1.0
        elif x_position == 1 or x_position == 6:
            return 1.0
        elif x_position == 2 or x_position == 5:
            return 1.0
        elif x_position == 3 or x_position == 4:
            return 2.0

    def update_action_value_pairs(self):

        leftward = [-1, -1]
        rightward = [1, -1]

        #print(self.player_agent.get_current_moveable_pieces())

        for piece in self.player_agent.get_current_moveable_pieces():
            new_leftward_position = [x + y for x, y in zip(piece, leftward)]  # new leftward movement position
            self.append_action_value_pair(piece, new_leftward_position)
            new_rightward_position = [x + y for x, y in zip(piece, rightward)]  # new rightward movement position
            self.append_action_value_pair(piece, new_rightward_position)

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
            self.action_value_pairs.append(Action_Value_Pair(Move(old_position, new_position, self.player_agent, 1, 0), 1))
        else:
            return
