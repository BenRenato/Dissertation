from Checkers.Enums import Team, Direction
import random

# This class is a data representation of a real life player.
# The methods here are used to track pieces owned, generate random moves, and track various player statistics
# such as win rates, player types, and what side they're playing.

class Player:

    def __init__(self, is_black, player_type):

        self._is_black = is_black
        self._player_type = player_type
        self._current_pieces = []
        self._current_moveable_pieces = []

        self._last_hundred_games = []
        self._games_played = 0
        self._games_won = 0
        self._games_lost = 0

        self.init_player_vars()

    #----INIT METHODS----#
    def init_player_vars(self):
        self._init_current_moveable_pieces()

        self._init_current_pieces_on_board()

    def _init_current_pieces_on_board(self):
        self._current_pieces.clear()

        for i in range(8):
            if i % 2 == 0:
                if self._is_black:
                    # add to current pieces
                    self._current_pieces.append([i, 5])
                    self._current_pieces.append([i, 7])

                else:
                    self._current_pieces.append([i, 1])

            else:
                if self._is_black:
                    self._current_pieces.append([i, 6])

                else:
                    self._current_pieces.append([i, 0])
                    self._current_pieces.append([i, 2])

    def _init_current_moveable_pieces(self):

        if self._is_black:
            self._current_moveable_pieces = [[0, 5], [2, 5], [4, 5], [6, 5]]

        else:
            self._current_moveable_pieces = [[1, 2], [3, 2], [5, 2], [7, 2]]

    #----CLASS ATTRIBUTE METHODS----#
    def __str__(self):
        if self._is_black:
            return "Black"

        else:
            return "White"

    #----GETTERS AND SETTERS----#
    def get_current_moveable_pieces(self):
        return self._current_moveable_pieces

    def get_player_type(self):
        return self._player_type

    def get_current_pieces(self):
        return self._current_pieces

    def get_number_of_pieces_on_board(self):
        return len(self._current_pieces)

    def update_moveable_pieces(self, updated_list):
        self._current_moveable_pieces = updated_list

    def get_team(self):
        if self._is_black:
            return Team.BLACK

        else:
            return Team.WHITE

    def print_current_pieces(self):
        print(sorted(self._current_pieces))

    def get_number_of_current_moveable_pieces(self):
        return len(self._current_moveable_pieces)

    def get_games_played(self):
        return self._games_played

    def get_games_lost(self):
        return self._games_lost

    def get_games_won(self):
        return self._games_won

    def get_last_10_games(self):
        return self._last_hundred_games

    #----PLAYER STATISTICS TRACKERS OR MODIFIERS----#
    def increment_games_won(self):
        self._games_won += 1

    def increment_games_lost(self):
        self._games_lost += 1

    def increment_games_played(self):
        self._games_played += 1

    def add_result_to_last_10_games(self, outcome):
        if len(self._last_hundred_games) == 100:
            del self._last_hundred_games[0]

        self._last_hundred_games.append(outcome)

    def calculate_WRs(self):
        return self.calculate_WR_overall(), self.calculate_WR_past_10_games()

    def calculate_WR_overall(self):
        games_played = self._games_won + self._games_lost

        return (self._games_won / games_played) * 100

    def calculate_WR_past_10_games(self):
        if len(self._last_hundred_games) == 100:
            wins = 0

            for outcome in self.get_last_10_games():
                if outcome == outcome.WIN:
                    wins += 1

            return (wins / 100) * 100

        else:
            return 0

    def remove_taken_piece(self, piece):
        try:
            self._current_pieces.remove(self._current_pieces[self._current_pieces.index(piece)])

        except ValueError:
            return

    def _update_current_pieces(self, startpiece, endpiece):
        self._current_pieces.remove(self._current_pieces[self._current_pieces.index(startpiece)])

        self._current_pieces.append(endpiece)


class RandomPlayer(Player):

    def __init__(self, is_black, player_type):
        # Call super init to inherit members
        Player.__init__(self, is_black, player_type)

        self.chosen_piece = None
        self.chosen_piece_move_to = None

    #----RANDOM SELECTION METHODS----#
    def choose_random_start_position(self):
        self.chosen_piece = random.choice(self._current_moveable_pieces)

        return self.chosen_piece

    def choose_random_end_position(self, start_position):
        temp_position = start_position

        direction = random.choice([Direction.RIGHT, Direction.LEFT])

        if self._is_black:
            temp_position[1] -= 1

        else:
            temp_position[1] += 1

        if direction == Direction.LEFT:
            temp_position[0] -= 1

        elif direction == Direction.RIGHT:
            temp_position[0] += 1

        self.chosen_piece_move_to = temp_position

        return self.chosen_piece_move_to



