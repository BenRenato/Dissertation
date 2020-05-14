from time import sleep
from multiprocessing import Process, Queue
from Checkers.Enums import Team, Outcome
from Checkers.Move import Move
from Checkers_Agent.state_action_pair import State_Action_Pair
from Checkers_Agent.action_value_pair import Action_Value_Pair
from Metrics.Environment_Metrics import Env_Metrics
from copy import deepcopy
import random as rand
from math import exp, factorial


# TODO need to make new_agent_vs_agent_game() in game() to accomodate the white agent

class CheckersEnv:

    # start state, available moves, all same reward, randomly select move, move into state, use policy above to adjust reward,
    # keep track of moves made, further update value of moves if we win/lose, game starts again with a bit new knowledge

    # predictive search of best moves for the state, e.g minmax on the best moves we found in the previous game

    # learning rate, after x games we can reduce the swing of the updates to smaller increments

    def __init__(self, heuristics_only=True):

        self.state_action_value_pairs = []
        self.learning_rate = 10.0
        self.player_agent = None
        self.current_state = None
        self.action_value_pairs = []
        self.current_game_moves = []
        self.games_played = 0
        self.games_won = 0
        self.games_lost = 0
        self.write_to_file_tracker = 1
        self.first_write_to_file = True
        self.heuristic_mode = heuristics_only
        self.Env_Metrics = Env_Metrics()

        self.Env_Metrics.delete_previous_data()

    def calculate_best_move(self):

        possible_action_values = []

        self.update_action_value_pairs()

        self.create_action_value_pair_values(possible_action_values)

        matching_action_pair = self.check_state_seen_before()

        # This was an attempt at creating some multiprocessing for the functions where most of the time is spent.
        # create_pair_return_value = Queue()
        # check_state_return_value = Queue()
        # m1 = Process(target=self.check_state_seen_before, args=(check_state_return_value,))
        # m2 = Process(target=self.create_action_value_pair_values, args=(create_pair_return_value,))
        # m1.start()
        # m2.start()
        # m1.join()
        # m2.join()
        # matching_action_pair = check_state_return_value.get()
        # possible_action_values = create_pair_return_value.get()

        if matching_action_pair is not None:
            possible_action_values.append(matching_action_pair)

        best_move = self.evaluate_best_move(possible_action_values)

        new_state_action_value_pair = State_Action_Pair(deepcopy(self.current_state.get_board()), best_move)

        if not self.heuristic_mode:
            self.current_game_moves.append(new_state_action_value_pair)

        return best_move.get_action()

    def create_action_value_pair_values(self, possible_action_values):

        for pair in self.get_action_value_pairs():
            temp_state = deepcopy(self.current_state)
            action_to_evaluate = pair.get_action()

            if action_to_evaluate.makemove(temp_state):
                state_value = self.state_value_from_policy(temp_state)
                possible_action_values.append(Action_Value_Pair(action_to_evaluate, state_value))
            else:
                pass

    def check_state_seen_before(self):

        if self.state_action_value_pairs:

            current_match = None
            for pair in self.state_action_value_pairs:
                if pair.compare_to_current_board(self.current_state.get_board()):
                    if current_match is None:
                        current_match = pair.get_action_pair()
                    elif pair.get_action_pair().get_value() > current_match.get_value():
                        current_match = pair.get_action_pair()
                    else:
                        pass

            return current_match

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

        black_furthest_back_piece = self.calculate_lagging_piece(state)

        white_furthest_back_piece = self.calculate_lagging_piece(state)

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

        if self.player_agent.get_team() == Team.BLACK:
            return a2 + b2 + ((c2 - c1) ** 2) - (d2 ** 2)
        elif self.player_agent.get_team() == Team.WHITE:
            return a1 + b1 + ((c1 - c2) ** 2) - (d1 ** 2)

    def calculate_distance_to_other_side(self, y_position, side):

        if y_position == 0 or y_position == 1:
            if side == Team.BLACK:
                return 1.0
            elif side == Team.WHITE:
                return 0.0
        elif y_position == 2 or y_position == 3:
            if side == Team.BLACK:
                return 0.0
            elif side == Team.WHITE:
                return 0.0
        elif y_position == 4 or y_position == 5:
            if side == Team.BLACK:
                return 0.0
            elif side == Team.WHITE:
                return 0.0
        elif y_position == 6 or y_position == 7:
            if side == Team.BLACK:
                return 0.0
            elif side == Team.WHITE:
                return 1.0

    # Update state_space data based on win/lose
    def post_game_heuristics(self, outcome):
        self.used_too_much_ram()
        if not self.heuristic_mode:
            self.update_current_game_state_action_value_pairs(outcome)
        self.integrate_last_game_moves_to_state_space()
        self.reset_current_games_moves()

    def update_current_game_state_action_value_pairs(self, outcome):
        update_value_by = self.learning_rate * 2

        for state_action_value_pair in self.current_game_moves:
            cur_val = state_action_value_pair.get_action_pair().get_value()
            action_pair = state_action_value_pair.get_action_pair()

            if outcome == outcome.WIN:
                action_pair.update_value(cur_val + update_value_by)
                self.reinforce_move_that_captured(action_pair, 10)

            elif outcome == outcome.LOSE:
                state_action_value_pair.get_action_pair().update_value(cur_val - update_value_by)
                self.reinforce_move_that_captured(action_pair, 1)

            elif outcome == outcome.TIE:
                # Slight positive kick to tie moves
                state_action_value_pair.get_action_pair().update_value(cur_val + 0.5)
                self.reinforce_move_that_captured(action_pair, 5)

    def reinforce_move_that_captured(self, action_pair, value):
        if action_pair.get_action().get_took_enemy_piece():
            action_pair.update_value(value * self.learning_rate)

    def integrate_last_game_moves_to_state_space(self):

        self.state_action_value_pairs.extend(self.current_game_moves)

    def calculate_distance_from_centre(self, x_position):

        if x_position == 0 or x_position == 7:
            return -2.0
        elif x_position == 1 or x_position == 6:
            return 1.0
        elif x_position == 2 or x_position == 5:
            return 1.5
        elif x_position == 3 or x_position == 4:
            return 2.0

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

        if self.write_to_file_tracker == 100:
            WR, WR_10 = self.player_agent.calculate_WRs()
            self.Env_Metrics.write_env_data_to_file(WR, WR_10, self.player_agent.get_games_played()
                                                    , self.player_agent.get_team(), len(self.state_action_value_pairs))
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

    def reset_current_games_moves(self):

        self.current_game_moves.clear()

    def update_games_and_win_or_lose(self, outcome):

        self.player_agent.increment_games_played()

        if outcome == outcome.WIN:
            self.player_agent.increment_games_won()
        elif outcome == outcome.LOSE:
            self.player_agent.increment_games_lost()

        self.player_agent.add_result_to_last_10_games(outcome)
        self.increment_file_write_tracker()

    def get_current_state_action_value_pairs(self):

        return self.state_action_value_pairs

    def used_too_much_ram(self):

        defined_memory = 2048

        if self.Env_Metrics.get_ram_footprint() > defined_memory:
            print("More than {} used, culling cached state_space...".format(defined_memory))
            WR, WR_10 = self.player_agent.calculate_WRs()
            self.Env_Metrics.write_env_data_to_file(WR, WR_10, self.player_agent.get_games_played(),
                                                    self.player_agent.get_team(), len(self.state_action_value_pairs))
            self.Env_Metrics.cull_cached_state_space(self.get_current_state_action_value_pairs())
        else:
            pass
