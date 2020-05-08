from Checkers.CheckerBoard import CheckerBoard as checkboard
from Checkers.Player import Player as player
from Checkers.Player import RandomPlayer as randplayer
from Checkers.Move import Move as move
from Checkers.Enums import Player_Types as pt
from Checkers_Agent.checkers_env import CheckersEnv as env
import random
from time import sleep
from sys import exit


class Game:

    def __init__(self, player1_type, player2_type):

        self.board = checkboard(8, 8)

        # Player 1
        if player1_type == pt.HUMAN:
            self.player1 = player(False, pt.HUMAN)
        elif player1_type == pt.RANDOM:
            self.player1 = randplayer(False, pt.RANDOM)

        # Player 2
        if player2_type == pt.HUMAN:
            self.player2 = player(True, pt.HUMAN)
        elif player2_type == pt.AI:
            self.player2 = player(True, pt.AI)
            self.env = env()
        elif player2_type == pt.RANDOM:
            self.player2 = randplayer(True, pt.RANDOM)

        self.piece_to_move = None
        self.piece_move_to = None
        self.current_turn = None
        self.init_agent = True

    def run(self):
        self.board.setupdefaultboard()
        self.board.printboard()

        self.current_turn = random.choice([self.player1, self.player2])

        # TODO change the game logic for each type of game to a method so we dont have to check
        # TODO the player types every turn

        while 1:

            if self.check_terminal_state():
                # TODO pass current state and give "winner"
                exit("No moves left for a player.")

            print(str(self.current_turn) + " turn: \n")

            # Player input
            if self.player1.player_type == pt.HUMAN and self.player2.player_type == pt.HUMAN:
                self.take_player_input()

                # Turn coords into keys
                while True:
                    try:
                        self.check_if_exit()
                        self.input_to_coordinates()
                        self.send_move_request()
                    # TODO should probably change exception to ValueError, TypeError etc for performance reasons
                    except Exception:
                        print("Wrong format")
                        self.take_player_input()
                        continue
                    else:
                        break

            elif self.player1.player_type == pt.RANDOM and self.player2.player_type == pt.RANDOM:

                self.get_random_move()
                self.send_move_request()

            elif self.player1.player_type == pt.RANDOM and self.player2.player_type == pt.AI:

                if self.init_agent:
                    self.agent_vs_random_loop_init()
                    self.init_agent = False

                if self.current_turn == self.player2:
                    # TODO dont copy board or player done, move move_to_make.makemove below to own method and add where necessary above
                    # TODO send the best move to env.step(self.env.calculate_best_move()), then have step() act upon the reference
                    # TODO to the original board
                    #print("Board before calling agent_move_and_update()\n")
                    #self.board.printboard()
                    #self.player2.printcurrentpieces()
                    agent_selected_move = self.agent_move_and_update()
                    #print("Board after calling agent_move_and_update()\n")
                    #self.board.printboard()
                    #self.player2.printcurrentpieces()
                    self.piece_to_move = agent_selected_move.get_start_position()
                    self.piece_move_to = agent_selected_move.get_end_position()

                    if self.send_move_request():
                        pass
                    else:
                        print(agent_selected_move)
                        print("AI move request failed. Possible bug in action_value movement")
                        sleep(10)

                    sleep(1)

                elif self.current_turn == self.player1:
                    self.get_random_move()
                    self.send_move_request()
                    sleep(1)

    def send_move_request(self):

        move_request = move(self.piece_to_move, self.piece_move_to, self.current_turn, 1, 1)

        if move_request.makemove(self.board):
            self.update_game_after_move()
            return True
        else:
            print("Move failed")
            return False

    def agent_vs_random_loop_init(self):
        print("Random vs AI Agent")

        self.env.init_env_vars(self.board, self.player2)

    def agent_move_and_update(self):

        agent_move = self.env.calculate_best_move()
        agent_move.set_update_pieces_value(1)

        return agent_move

    def update_current_pieces_for_non_turn_player(self):

        if self.current_turn == self.player1:
            self.player2.remove_taken_piece(self.piece_move_to)
        else:
            self.player1.remove_taken_piece(self.piece_move_to)

    def update_moveable_pieces(self):

        current_black_pieces_on_board = self.player2.get_current_pieces()  # player 2 is black
        current_white_pieces_on_board = self.player1.get_current_pieces()  # player 1 is white

        black_moveable_pieces = []
        white_moveable_pieces = []

        deltaPositionsBlack = [[-1, -1], [1, -1]]
        deltaPositionsWhite = [[-1, 1], [1, 1]]

        for coord in current_black_pieces_on_board:
            # (horizontalPos, verticalPos)
            # TODO METHODIFY THIS
            for i in range(2):
                tempEndPosition = [a + b for a, b in zip(coord, deltaPositionsBlack[i])]
                isMoveable = move(coord, tempEndPosition, self.player2, 0)
                if isMoveable.makemove(self.board):
                    black_moveable_pieces.append(coord)
                    break
                else:
                    continue

        for coord in current_white_pieces_on_board:
            # (horizontalPos, verticalPos)
            for i in range(2):
                tempEndPosition = [a + b for a, b in zip(coord, deltaPositionsWhite[i])]
                isMoveable = move(coord, tempEndPosition, self.player1, 0)
                if isMoveable.makemove(self.board):
                    white_moveable_pieces.append(coord)
                    break
                else:
                    continue

        self.player1.update_moveable_pieces(white_moveable_pieces)
        self.player2.update_moveable_pieces(black_moveable_pieces)

    def input_to_coordinates(self):

        # TODO try catch here
        self.piece_to_move = [int(s) for s in self.piece_to_move.split(',')]
        self.piece_move_to = [int(s) for s in self.piece_move_to.split(',')]

    def get_random_move(self):

        self.piece_to_move = self.current_turn.choose_random_start_position()
        self.piece_move_to = self.current_turn.choose_random_end_position(self.piece_to_move.copy())

    def check_if_exit(self):
        if self.piece_move_to.lower() == 'exit':
            exit(1)
        else:
            return

    def update_current_turn(self):

        if self.current_turn == self.player1:
            self.current_turn = self.player2
        else:
            self.current_turn = self.player1

    def check_terminal_state(self):

        if self.player1 is None or self.player2 is None:
            return False

        if self.player1.get_number_of_current_moveable_pieces() == 0 or self.player2.get_number_of_current_moveable_pieces() == 0:
            return True

    def get_player(self, player):

        if player == 1:
            return self.player1
        else:
            return self.player2

    def get_boardstate(self):
        return self.board

    def take_player_input(self):
        self.piece_to_move = input("Piece to move? Format: x, y ")
        self.piece_move_to = input("Move to where? Format: x, y \n'exit' to exit: ")

    def update_game_after_move(self):
        self.update_current_pieces_for_non_turn_player()
        self.board.printboard()
        self.update_moveable_pieces()
        self.update_current_turn()
        print("\n")
