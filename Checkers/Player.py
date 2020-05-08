from Checkers import Enums
import random

class Player:

    def __init__(self, isBlack, player_type):
        self.isblack = isBlack
        self.player_type = player_type
        self.currentpieces = []
        self.current_moveable_pieces = []

        #set current moveable pieces for each side
        if isBlack:
            self.current_moveable_pieces = [[0, 5], [2, 5], [4, 5], [6, 5]]
        else:
            self.current_moveable_pieces = [[1, 2], [3, 2], [5, 2], [7, 2]]


        for i in range(8):
            if i % 2 == 0:
                if self.isblack:
                    #add to current pieces
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

    def update_moveable_pieces(self, updatedlist):

        self.current_moveable_pieces = updatedlist

    def get_team(self):

        if self.isblack:
            return Enums.Team.BLACK
        else:
            return Enums.Team.WHITE

    def remove_taken_piece(self, piece):

        try:
            self.currentpieces.remove(self.currentpieces[self.currentpieces.index(piece)])
        except ValueError:
            return

    def updatecurrentpieces(self, startpiece, endpiece):

        print("Removing " + str(self.currentpieces[self.currentpieces.index(startpiece)]))
        print("Before removal " + str(sorted(self.currentpieces)))
        self.currentpieces.remove(self.currentpieces[self.currentpieces.index(startpiece)])
        print("After removal " + str(sorted(self.currentpieces)))

        print("Appending " + str(endpiece))
        self.currentpieces.append(endpiece)
        print("After appending: " + str(sorted(self.currentpieces)))

    def printcurrentpieces(self):
        print(sorted(self.currentpieces))

    def get_number_of_current_moveable_pieces(self):
        return len(self.current_moveable_pieces)

    def terminal_moveable_pieces_state(self):

        if self.get_number_of_current_moveable_pieces() == 0:
            return True
        else:
            return False

class RandomPlayer(Player):

    def __init__(self, isBlack, player_type):
        #Call super init to inherit members
        Player.__init__(self, isBlack, player_type)
        self.chosen_piece = None
        self.chosen_piece_move_to = None

    def choose_random_start_position(self):

        self.chosen_piece = random.choice(self.current_moveable_pieces)
        return self.chosen_piece


    def choose_random_end_position(self, start_position):

        temp_position = start_position

        direction = random.choice([Enums.Direction.RIGHT, Enums.Direction.LEFT])

        if self.isblack:
            temp_position[1] -= 1
        else:
            temp_position[1] += 1

        if direction == Enums.Direction.LEFT:
            temp_position[0] -= 1
        elif direction == Enums.Direction.RIGHT:
            temp_position[0] += 1

        self.chosen_piece_move_to = temp_position

        return self.chosen_piece_move_to
