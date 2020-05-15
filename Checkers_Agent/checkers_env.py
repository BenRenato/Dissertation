from multiprocessing import Process, Queue
from Checkers.Enums import Team, Outcome
from Checkers.Move import Move
from Checkers_Agent.StateActionPair import StateActionPair
from Checkers_Agent.ActionValuePair import ActionValuePair
from Metrics.Environment_Metrics import EnvMetrics
from copy import deepcopy
import random as rand


# This class is used to initialise an agent, caluclate state policy values, make decisions on which moves to make,
# also responsible for reinforcement algorithm methods.

class CheckersEnv:

    # Start state, available moves, all same reward, randomly select move, move into state, use policy above to adjust reward,
    # keep track of moves made, further update value of moves if we win/lose, game starts again with a bit new knowledge
    def __init__(self, heuristics_only=True):

        self._state_action_value_pairs = []
        self._action_value_pairs = []
        self._current_game_moves = []

        self._learning_rate = 10.0

        self._player_agent = None
        self._current_state = None

        self._write_to_file_tracker = 1
        self._first_write_to_file = True
        self._env_metrics = EnvMetrics()
        self._env_metrics.delete_previous_data()

        self._heuristic_mode = heuristics_only

    #----CUSTOM INIT METHODS----#
    def init_env_vars(self, board, player):
        self.set_current_state(board)

        self.set_player(player)

        self._reset_action_value_pairs()

    #----CALCULATION OF MOVE VALUE METHODS----#
    def calculate_best_move(self):
        possible_action_values = []

        self._update_action_value_pairs()

        self._create_action_value_pair_values(possible_action_values)

        matching_action_pair = self._check_state_seen_before()

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

        best_move = self._evaluate_best_move(possible_action_values)

        new_state_action_value_pair = StateActionPair(deepcopy(self._current_state.get_board()), best_move)

        if not self._heuristic_mode:
            self._current_game_moves.append(new_state_action_value_pair)

        return best_move.get_action()

    def _check_state_seen_before(self):
        if self._state_action_value_pairs:
            current_match = None

            for pair in self._state_action_value_pairs:
                if pair.compare_to_current_board(self._current_state.get_board()):
                    if current_match is None:
                        current_match = pair.get_action_pair()

                    elif pair.get_action_pair().get_value() > current_match.get_value():
                        current_match = pair.get_action_pair()

                    else:
                        pass

            return current_match

    #----POLICY CALUCLATION METHODS----#
    def _evaluate_best_move(self, action_pairs):
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

    def _state_value_from_policy(self, state):
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

        black_furthest_back_piece = self._calculate_lagging_piece(state)

        white_furthest_back_piece = self._calculate_lagging_piece(state)

        for i in range(state.get_x()):
            for j in range(state.get_y()):
                if state[i, j].get_occupier().get_team() == Team.BLACK:
                    black_sum_distance_to_other_side += self._calculate_distance_to_other_side(j, Team.BLACK)

                    black_sum_of_distance_to_centre += self._calculate_distance_from_centre(i)

                    black_counters_on_board += 1

                elif state[i, j].get_occupier().get_team() == Team.WHITE:
                    white_sum_distance_to_other_side += self._calculate_distance_to_other_side(j, Team.WHITE)

                    white_sum_distance_to_centre += self._calculate_distance_from_centre(i)

                    white_counters_on_board += 1

        state_value = self._calculate_policy_with_current_values(black_sum_distance_to_other_side,
                                                                 white_sum_distance_to_other_side
                                                                 , black_sum_of_distance_to_centre,
                                                                 white_sum_distance_to_centre
                                                                 , black_counters_on_board, white_counters_on_board,
                                                                 white_furthest_back_piece, black_furthest_back_piece)

        return state_value

    def _calculate_lagging_piece(self, state):
        difference_in_advancement_of_pieces = 0

        current_pieces = self._player_agent.get_current_pieces()

        most_advanced_piece_y_axis = None
        least_advanced_piece_y_axis = None

        if len(current_pieces) >= 2:
            for i in range(state.get_x()):
                for j in range(state.get_y()):
                    if state[i, j].get_occupier().get_team() == self._player_agent.get_team():
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

    def _calculate_policy_with_current_values(self, a1, a2, b1, b2, c1, c2, d1, d2):
        if self._player_agent.get_team() == Team.BLACK:
            return a2 + b2 + ((c2 - c1) ** 2) - (d2 ** 2)

        elif self._player_agent.get_team() == Team.WHITE:
            return a1 + b1 + ((c1 - c2) ** 2) - (d1 ** 2)

    # Ignore PyCharm suggesting static method, we don't want to call this without a class instance
    def _calculate_distance_to_other_side(self, y_position, side):
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

    def _calculate_distance_from_centre(self, x_position):
        if x_position == 0 or x_position == 7:
            return -2.0

        elif x_position == 1 or x_position == 6:
            return 1.0

        elif x_position == 2 or x_position == 5:
            return 1.5

        elif x_position == 3 or x_position == 4:
            return 2.0

    def _create_action_value_pair_values(self, possible_action_values):
        for pair in self.get_action_value_pairs():
            temp_state = deepcopy(self._current_state)

            action_to_evaluate = pair.get_action()

            if action_to_evaluate.make_move(temp_state):
                state_value = self._state_value_from_policy(temp_state)

                possible_action_values.append(ActionValuePair(action_to_evaluate, state_value))

            else:
                pass

    #----REINFORCEMENT RELATED METHODS----#
    # Update state_space data based on win/lose
    def post_game_heuristics(self, outcome):
        self._used_too_much_ram()

        if not self._heuristic_mode:
            self._update_current_game_state_action_value_pairs(outcome)

            self._integrate_last_game_moves_to_state_space()

            self._reset_current_games_moves()

    def _reinforce_move_that_captured(self, action_pair, value):
        if action_pair.get_action().get_took_enemy_piece():
            action_pair.update_value(value * self._learning_rate)

    def update_games_and_win_or_lose(self, outcome):
        self._player_agent.increment_games_played()

        if outcome == outcome.WIN:
            self._player_agent.increment_games_won()

        elif outcome == outcome.LOSE:
            self._player_agent.increment_games_lost()

        self._player_agent.add_result_to_last_10_games(outcome)

        self._increment_file_write_tracker()

    def _integrate_last_game_moves_to_state_space(self):
        self._state_action_value_pairs.extend(self._current_game_moves)

    def _update_current_game_state_action_value_pairs(self, outcome):
        update_value_by = self._learning_rate * 2

        for state_action_value_pair in self._current_game_moves:
            cur_val = state_action_value_pair.get_action_pair().get_value()

            action_pair = state_action_value_pair.get_action_pair()

            if outcome == outcome.WIN:
                action_pair.update_value(cur_val + update_value_by)

                self._reinforce_move_that_captured(action_pair, 10)

            elif outcome == outcome.LOSE:
                state_action_value_pair.get_action_pair().update_value(cur_val - update_value_by)

                self._reinforce_move_that_captured(action_pair, 1)

            elif outcome == outcome.TIE:
                # Slight positive kick to tie moves
                state_action_value_pair.get_action_pair().update_value(cur_val + 0.5)

                self._reinforce_move_that_captured(action_pair, 5)

    #----SETTERS AND GETTERS----#
    def _update_action_value_pairs(self):
        leftward = []
        rightward = []

        if self._player_agent.get_team() == Team.BLACK:
            leftward = [-1, -1]
            rightward = [1, -1]

        elif self._player_agent.get_team() == Team.WHITE:
            leftward = [-1, 1]
            rightward = [1, 1]

        self._reset_action_value_pairs()

        for piece in self._player_agent.get_current_moveable_pieces():
            new_leftward_position = [x + y for x, y in zip(piece, leftward)]  # new leftward movement position

            self._append_action_value_pair(piece, new_leftward_position)

            new_rightward_position = [x + y for x, y in zip(piece, rightward)]  # new rightward movement position

            self._append_action_value_pair(piece, new_rightward_position)

    def _append_action_value_pair(self, old_position, new_position):
        if 0 <= new_position[0] < 8 and 0 <= new_position[1] < 8:
            self._action_value_pairs.append(
                ActionValuePair(Move(old_position, new_position, self._player_agent, 1, 0), 1))

        else:
            return

    def set_player(self, player):
        self._player_agent = player

    def set_current_state(self, board):
        self._current_state = board

    def _reset_action_value_pairs(self):
        self._action_value_pairs = []

    def get_action_value_pairs(self):
        return self._action_value_pairs

    def print_action_value_pairs(self):
        print(self._action_value_pairs)

    def _reset_current_games_moves(self):
        self._current_game_moves.clear()

    def get_current_state_action_value_pairs(self):
        return self._state_action_value_pairs

    #----FILE RECORDING METHODS----#
    def _increment_file_write_tracker(self):
        if self._write_to_file_tracker == 100:
            WR, WR_10 = self._player_agent.calculate_WRs()

            self._env_metrics.write_env_data_to_file(WR, WR_10, self._player_agent.get_games_played()
                                                     , self._player_agent.get_team(),
                                                     len(self._state_action_value_pairs))

            self._write_to_file_tracker = 0

        self._write_to_file_tracker += 1

    #----OS TRACKING METHODS----#
    def _used_too_much_ram(self):
        defined_memory = 2048

        if self._env_metrics.get_ram_footprint() > defined_memory:
            print("More than {} used, culling cached state_space...".format(defined_memory))

            WR, WR_10 = self._player_agent.calculate_WRs()

            self._env_metrics.write_env_data_to_file(WR, WR_10, self._player_agent.get_games_played(),
                                                     self._player_agent.get_team(), len(self._state_action_value_pairs))

            self._env_metrics.cull_cached_state_space(self.get_current_state_action_value_pairs())

        else:
            pass











