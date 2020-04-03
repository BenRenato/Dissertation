from Checkers.CheckerBoard import CheckerBoard as checkboard
from Checkers.Player import Player as player
from Checkers.Player import RandomPlayer as randplayer
from Checkers.Move import Move as move
import random
from time import sleep
from sys import exit


class Game():

    def __init__(self, player1_type, player2_type):

        self.board = checkboard(8, 8)

        # TODO clean up, make them Enums
        if player1_type == "human":
            self.player1 = player(True, "human")
        elif player1_type == "CPU":
            self.player1 = player(True, "CPU")
        elif player1_type == "random":
            self.player1 = randplayer(True, "random")

        if player2_type == "human":
            self.player2 = player(False, "human")
        elif player2_type == "CPU":
            self.player2 = player(True, "CPU")
        elif player2_type == "random":
            self.player2 = randplayer(False, "random")

        self.piece_to_move = None
        self.piece_move_to = None
        self.current_turn = None

    def run(self):
        self.board.setupdefaultboard()
        self.board.printboard()

        self.current_turn = random.choice([self.player1, self.player2])

        # TODO clean this up, it's gross. Add input validation.
        while 1:

            print(str(self.current_turn) + " turn: \n")

            # Player input
            if self.player1.player_type == "human" and self.player2.player_type == "human":
                self.piece_to_move = input("Piece to move? Format: x, y ")
                self.piece_move_to = input("Move to where? Format: x, y \n'exit' to exit: ")

                # Turn coords into keys
                while True:
                    try:

                        if self.piece_move_to.lower() == 'exit':
                            exit(1)

                        self.piece_to_move = [int(s) for s in self.piece_to_move.split(',')]
                        self.piece_move_to = [int(s) for s in self.piece_move_to.split(',')]

                    # TODO should probably change exception to ValueError, TypeError etc for performance reasons
                    except Exception:
                        print("Wrong format")
                        self.piece_to_move = input("Piece to move? Format: x, y  ")
                        self.piece_move_to = input("Move to where? Format: x, y  ")
                        continue
                    else:
                        break
            elif self.player1.player_type == "human" and self.player2.player_type == "random":
                print("Human vs Random")
                exit(1)
            elif self.player1.player_type == "random" and self.player2.player_type == "random":

                self.piece_to_move = self.current_turn.choose_random_start_position()

                self.piece_move_to = self.current_turn.choose_random_end_position(self.piece_to_move.copy())

                sleep(1)

            elif self.player1.player_type == "human" and self.player2.player_type == "CPU":
                print("Human vs AI Agent")
                exit(1)

            move_to_make = move(self.piece_to_move, self.piece_move_to, self.current_turn)
            if move_to_make.makemove(self.board):

                self.update_current_pieces_for_non_turn_player()
                self.update_current_turn()
                print("\n")
                self.board.printboard()
                #sleep(0.5)
            else:
                pass

    def update_current_pieces_for_non_turn_player(self):
        if self.current_turn == self.player1:
            self.player2.remove_taken_piece(self.piece_move_to)
        else:
            self.player1.remove_taken_piece(self.piece_move_to)

    def update_moveable_piece_this_turn(self):
        #TODO update if moveable
        pass


    def update_current_turn(self):

        if self.current_turn == self.player1:
            self.current_turn = self.player2
        else:
            self.current_turn = self.player1

    def check_row_behind_moved_piece(self):
        #TODO check if moved piece freed up other pieces to move
        pass