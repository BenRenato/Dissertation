from Checkers.Enums import Team, Direction
import random


class Player:

    def __init__(self, isBlack, player_type):
        self.isblack = isBlack
        self.player_type = player_type
        self.currentpieces = []
        self.current_moveable_pieces = []

        self.last_ten_games = []
        self.games_played = 0
        self.games_won = 0
        self.games_lost = 0

        self.init_player_vars()

    def init_player_vars(self):
        self.init_current_moveable_pieces()

        self.init_current_pieces_on_board()

    def init_current_pieces_on_board(self):

        # TODO change this to a hard coded set of pieces like init_current_moveable_pieces

        self.currentpieces.clear()

        for i in range(8):
            if i % 2 == 0:
                if self.isblack:
                    # add to current pieces
                    self.currentpieces.append([i, 5])
                    self.currentpieces.append([i, 7])

                else:
                    self.currentpieces.append([i, 1])
            else:
                if self.isblack:
                    self.currentpieces.append([i, 6])
                else:
                    self.currentpieces.append([i, 0])
                    self.currentpieces.append([i, 2])

    def init_current_moveable_pieces(self):

        if self.isblack:
            self.current_moveable_pieces = [[0, 5], [2, 5], [4, 5], [6, 5]]
        else:
            self.current_moveable_pieces = [[1, 2], [3, 2], [5, 2], [7, 2]]

    def __str__(self):
        if self.isblack:
            return "Black"
        else:
            return "White"

    def get_current_moveable_pieces(self):
        return self.current_moveable_pieces

    def get_player_type(self):
        return self.player_type

    def get_current_pieces(self):
        return self.currentpieces

    def get_number_of_pieces_on_board(self):
        return len(self.currentpieces)

    def update_moveable_pieces(self, updatedlist):

        self.current_moveable_pieces = updatedlist

    def get_team(self):

        if self.isblack:
            return Team.BLACK
        else:
            return Team.WHITE

    def remove_taken_piece(self, piece):

        try:
            self.currentpieces.remove(self.currentpieces[self.currentpieces.index(piece)])
        except ValueError:
            return

    def updatecurrentpieces(self, startpiece, endpiece):

        # print("Removing " + str(self.currentpieces[self.currentpieces.index(startpiece)]))
        # print("Before removal " + str(sorted(self.currentpieces)))
        self.currentpieces.remove(self.currentpieces[self.currentpieces.index(startpiece)])
        # print("After removal " + str(sorted(self.currentpieces)))

        # print("Appending " + str(endpiece))
        self.currentpieces.append(endpiece)
        # print("After appending: " + str(sorted(self.currentpieces)))

    def printcurrentpieces(self):
        print(sorted(self.currentpieces))

    def get_number_of_current_moveable_pieces(self):
        return len(self.current_moveable_pieces)

    def terminal_moveable_pieces_state(self):

        if self.get_number_of_current_moveable_pieces() == 0:
            return True
        else:
            return False

    def get_games_played(self):
        return self.games_played

    def get_games_lost(self):
        return self.games_lost

    def get_games_won(self):
        return self.games_won

    def increment_games_won(self):
        self.games_won += 1

    def increment_games_lost(self):
        self.games_lost += 1

    def increment_games_played(self):
        self.games_played += 1

    def add_result_to_last_10_games(self, outcome):

        if len(self.last_ten_games) == 10:
            del self.last_ten_games[0]
            print("DELETED 0 INDEX")

        self.last_ten_games.append(outcome)


class RandomPlayer(Player):

    def __init__(self, isBlack, player_type):
        # Call super init to inherit members
        Player.__init__(self, isBlack, player_type)
        self.chosen_piece = None
        self.chosen_piece_move_to = None

    def choose_random_start_position(self):

        self.chosen_piece = random.choice(self.current_moveable_pieces)
        return self.chosen_piece

    def choose_random_end_position(self, start_position):

        temp_position = start_position

        direction = random.choice([Direction.RIGHT, Direction.LEFT])

        if self.isblack:
            temp_position[1] -= 1
        else:
            temp_position[1] += 1

        if direction == Direction.LEFT:
            temp_position[0] -= 1
        elif direction == Direction.RIGHT:
            temp_position[0] += 1

        self.chosen_piece_move_to = temp_position

        return self.chosen_piece_move_to



