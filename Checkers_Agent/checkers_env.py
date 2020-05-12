from time import sleep

from Checkers.Enums import Team, Outcome
from Checkers.Move import Move
from Checkers_Agent.state_action_pair import State_Action_Pair
from Checkers_Agent.action_value_pair import Action_Value_Pair
from copy import deepcopy
import random as rand
from math import exp, factorial
import psutil
import os


# TODO need to make new_agent_vs_agent_game() in game() to accomodate the white agent

class CheckersEnv:
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
        self.epsilon_greedy_value = 0.2  # 0.2 = 10% of the time pick a random action, 90% time greedy (rand.random can only produce 0.1-1.0)
        self.learning_rate = 1.0  # 1 = harsh punishments/big rewards. 0.1 = small punishments and small rewards
        self.player_agent = None
        self.current_state = None
        self.action_value_pairs = []
        self.games_played = 0
        self.games_won = 0
        self.games_lost = 0
        self.write_to_file_tracker = 0
        self.first_write_to_file = True

    def calculate_best_move(self):

        possible_action_values = []

        self.update_action_value_pairs()

        for pair in self.get_action_value_pairs():
            temp_state = deepcopy(self.current_state)
            action_to_evaluate = pair.get_action()

            if action_to_evaluate.makemove(temp_state):
                state_value = self.state_value_from_policy(temp_state)
                possible_action_values.append(Action_Value_Pair(action_to_evaluate, state_value))
            else:
                pass

        matching_action_pair = self.check_state_seen_before()

        if matching_action_pair is not None:
            possible_action_values.append(matching_action_pair)

        if rand.random() < self.epsilon_greedy_value:
            action = rand.choice(possible_action_values)
            return action.get_action()

        best_move = self.evaluate_best_move(possible_action_values)

        if matching_action_pair is None:
            self.state_action_value_pairs.append(State_Action_Pair(deepcopy(self.current_state.get_board()), best_move))

        return best_move.get_action()

    def check_state_seen_before(self):

        if self.state_action_value_pairs:

            for pair in self.state_action_value_pairs:
                if pair.compare_to_current_board(self.current_state.get_board()):
                    print("##### FOUND STATE PREVIOUSLY ####")
                    return pair.get_action_pair()

            else:
                print("No previous state found.")
                return None

        # Ignore PyCharm suggesting static method, we don't want to call this without a class instance

    def evaluate_best_move(self, action_pairs):

        best_move_so_far = None

        for move in action_pairs:

            if best_move_so_far is None:
                best_move_so_far = move
            elif move.get_value() > best_move_so_far.get_value():
                best_move_so_far = move
            elif move.get_value() == best_move_so_far.get_value():
                if rand.randint(0, 1) == 1:
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

        # Di

        black_furthest_back_piece = 0

        white_furthest_back_piece = 0

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

        black_furthest_back_piece = self.calculate_lagging_piece(state)

        white_furthest_back_piece = self.calculate_lagging_piece(state)

        state_value = self.calculate_policy_with_current_values(black_sum_distance_to_other_side,
                                                                white_sum_distance_to_other_side
                                                                , black_sum_of_distance_to_centre,
                                                                white_sum_distance_to_centre
                                                                , black_counters_on_board, white_counters_on_board,
                                                                white_furthest_back_piece, black_furthest_back_piece)
        return state_value

    def calculate_lagging_piece(self, state):

        difference_in_advancement_of_pieces = 0

        current_pieces = self.player_agent.get_current_pieces()

        most_advanced_piece_y_axis = None
        least_advanced_piece_y_axis = None

        if len(current_pieces) >= 2:
            # Wish I had template functions from C++ : - )
            # It's okay, for i, for j is still most Pythonic  : )
            for i in range(state.get_x()):
                for j in range(state.get_y()):
                    if state[i, j].getoccupier().team == self.player_agent.get_team():
                        if least_advanced_piece_y_axis is None:
                            least_advanced_piece_y_axis = j
                        elif j > least_advanced_piece_y_axis:
                            most_advanced_piece_y_axis = least_advanced_piece_y_axis
                            least_advanced_piece_y_axis = j
        else:
            print("Not enough pieces to perform differential comparison.")

        if least_advanced_piece_y_axis is not None and most_advanced_piece_y_axis is not None:
            difference_in_advancement_of_pieces += abs(most_advanced_piece_y_axis - least_advanced_piece_y_axis)

        return difference_in_advancement_of_pieces

    def calculate_policy_with_current_values(self, a1, a2, b1, b2, c1, c2, d1, d2):
        # Ve =  α(A2 − A1) +  α(B2 − B1) +  α(C1 - C2)
        # TODO tune the math here, maybe not factorial, could be square or just double etc

        try:
            d2 = factorial(d2)
            d1 = factorial(d1)
        except ValueError:
            d1 = 0
            d2 = 0
            print("Factorial failed, possibly negative.")

        if self.player_agent.get_team() == Team.BLACK:
            return (a2 - a1) + (b2 - b1) + (c1 - c2) - d2
        elif self.player_agent.get_team() == Team.WHITE:
            return (a1 - a2) + (b1 - b2) + (c2 - c1) - d1

    def calculate_distance_to_other_side(self, y_position, side):

        if y_position == 0 or y_position == 1:
            if side == Team.BLACK:
                return 1.0
            elif side == Team.WHITE:
                return -0.5
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
                return -0.5
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
            return 0.0
        elif x_position == 1 or x_position == 6:
            return 1.0
        elif x_position == 2 or x_position == 5:
            return 1.5
        elif x_position == 3 or x_position == 4:
            return 1.5

    def update_action_value_pairs(self):

        leftward = []
        rightward = []

        if self.player_agent.get_team() == Team.BLACK:
            leftward = [-1, -1]
            rightward = [1, -1]
        elif self.player_agent.get_team() == Team.WHITE:
            leftward = [-1, 1]
            rightward = [1, 1]

        self.reset_action_value_pairs()

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

    def reset_action_value_pairs(self):
        self.action_value_pairs = []

    def increment_file_write_tracker(self):

        if self.write_to_file_tracker == 10:
            self.write_env_data_to_file()
            self.write_to_file_tracker = 0

        self.write_to_file_tracker += 1

    def init_env_vars(self, board, player):
        self.set_current_state(board)
        self.set_player(player)
        self.reset_action_value_pairs()

    def get_action_value_pairs(self):
        return self.action_value_pairs

    def append_action_value_pair(self, old_position, new_position):
        if 0 <= new_position[0] < 8 and 0 <= new_position[1] < 8:
            self.action_value_pairs.append(
                Action_Value_Pair(Move(old_position, new_position, self.player_agent, 1, 0), 1))
        else:
            return

    def update_games_and_win_or_lose(self, outcome):

        self.increment_file_write_tracker()
        self.player_agent.increment_games_played()

        if outcome.WIN:
            self.player_agent.increment_games_won()
        elif outcome.LOSE:
            self.player_agent.increment_games_lost()

        self.player_agent.add_result_to_last_10_games(outcome)

    def get_current_state_action_value_pairs(self):

        return self.state_action_value_pairs

    def used_too_much_RAM(self):

        if self.get_RAM_footprint() > 2048:
            # TODO cull memory from agents here lmfao
            print("More than 2GB used, culling cached state_space...")
            sleep(5)
        else:
            pass

    def get_RAM_footprint(self):
        process = psutil.Process(os.getpid())
        footprint = process.memory_info().rss / 1024 / 1024
        print("RAM footprint is: " + str(footprint) + " MB")

        return footprint


    def write_env_data_to_file(self):
        # TODO also write best, worst, and average values to file
        # TODO also method the path exists stuff keep write logic

        winrate = 0

        winrate_10_games = 0

        RAM_usage = self.get_RAM_footprint()

        if os.path.exists("env_data.txt") and self.first_write_to_file:
            self.first_write_to_file = False
            print("Previous env data found, deleting...")
            open('env_data.txt', 'w').close()
            sleep(5)

        with open("env_data.txt", "a") as text_file:
            text_file.write("WR all/10 games: {:.2f}%/{:.2f}%\n"
                            "RAM usage: {}MB\n".format(winrate, winrate_10_games, RAM_usage))


    def cull_cached_state_space(self):
        # TODO iterate and cull
        pass
