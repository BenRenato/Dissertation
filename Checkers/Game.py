from Checkers.CheckerBoard import CheckerBoard as checkboard
from Checkers.Player import Player as player
from Checkers.Player import RandomPlayer as randplayer
from Checkers.Move import Move as move
from Checkers.Enums import Player_Types as pt
from Checkers.Enums import Outcome as oc
from Checkers.Enums import Game_Type as gt
from Checkers.Enums import Team
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
        elif player1_type == pt.HEURISTIC:
            self.player1 = player(False, pt.HEURISTIC)
            self.env_white = env()
        elif player1_type == pt.RANDOM:
            self.player1 = randplayer(False, pt.RANDOM)
        elif player1_type == pt.AI:
            self.player1 = player(False, pt.AI)
            self.env_white = env(False)

        # Player 2
        if player2_type == pt.HUMAN:
            self.player2 = player(True, pt.HUMAN)
        elif player2_type == pt.HEURISTIC:
            self.player2 = player(True, pt.HEURISTIC)
            self.env_black = env()
        elif player2_type == pt.RANDOM:
            self.player2 = randplayer(True, pt.RANDOM)
        elif player2_type == pt.AI:
            self.player2 = player(True, pt.AI)
            self.env_black = env(False)

        self.piece_to_move = None
        self.piece_move_to = None
        self.current_turn = None
        self.init_agent = True
        self.game_type = self.get_game_type()

    def run(self):
        self.board.setupdefaultboard()
        self.board.printboard()

        self.current_turn = random.choice([self.player1, self.player2])

        # TODO change the game logic for each type of game to a method so we dont have to check
        # TODO the player types every turn

        #TODO perform heustistics, change values of pairs, then play again, repeat until x amount of games, print WR, policy weights, etc after each game

        while 1:

            if self.check_terminal_state():

                winner = self.get_game_winner()

                print("The winner is " + str(winner) + ".")

                self.resolve_end_game_state_and_setup_next_game(self.game_type, winner)

                self.exit_game_after_X_games()

            print(str(self.current_turn) + " turn: \n")

            #TODO make the check for player_types be for game type
            # Player input
            if self.game_type == gt.PvP:
                self.take_player_input()

                # Turn coords into keys
                while True:
                    try:
                        self.check_if_exit()
                        self.input_to_coordinates()
                        self.send_move_request()
                    # TODO double check ValueError is enough
                    except ValueError:
                        print("Wrong format")
                        self.take_player_input()
                        continue
                    else:
                        break

            elif self.game_type == gt.RvR:

                self.get_random_move()
                self.send_move_request()

            elif self.game_type == gt.RvH:

                if self.init_agent:
                    self.env_black.init_env_vars(self.board, self.player2)
                    self.init_agent = False

                self.random_vs_agent_game()

            elif self.game_type == gt.HvH:

                if self.init_agent:
                    self.env_white.init_env_vars(self.board, self.player1)
                    self.env_black.init_env_vars(self.board, self.player2)
                    self.init_agent = False

                self.agent_vs_agent_game()

            elif self.game_type == gt.RvAI:
                pass

            elif self.game_type == gt.AIvAI:
                pass

    def exit_game_after_X_games(self):

        if self.player2.get_games_played() == 800:
            exit("100 games played")

    def resolve_end_game_state_and_setup_next_game(self, type, winner):

        if type == gt.RvH:
            if winner == Team.BLACK:
                self.new_random_vs_agent_game(oc.WIN)
                self.env_black.post_game_heuristics(oc.WIN, oc.LOSE)
            elif winner == Team.WHITE:
                self.new_random_vs_agent_game(oc.LOSE)
                self.env_black.post_game_heuristics(oc.LOSE, oc.WIN)
            else:
                self.new_random_vs_agent_game(oc.TIE)
                self.env_black.post_game_heuristics(oc.TIE, oc.TIE)

        elif type == gt.HvH:
            if winner == Team.BLACK:
                self.new_agent_vs_agent_game(oc.WIN, oc.LOSE)
                self.env_black.post_game_heuristics(oc.WIN, oc.LOSE)
                self.env_white.post_game_heuristics(oc.LOSE, oc.WIN)
            elif winner == Team.WHITE:
                self.new_agent_vs_agent_game(oc.LOSE, oc.WIN)
                self.env_black.post_game_heuristics(oc.WIN, oc.LOSE)
                self.env_white.post_game_heuristics(oc.LOSE, oc.WIN)
            else:
                self.new_agent_vs_agent_game(oc.TIE, oc.TIE)
                self.env_black.post_game_heuristics(oc.TIE, oc.TIE)
                self.env_white.post_game_heuristics(oc.TIE, oc.TIE)


    def get_game_type(self):

        white_type = self.player1.get_player_type()
        black_type = self.player2.get_player_type()

        if white_type == pt.HUMAN and black_type == pt.HUMAN:
            return gt.PvP
        elif white_type == pt.RANDOM and black_type == pt.RANDOM:
            return gt.RvR
        elif white_type == pt.RANDOM and black_type == pt.HEURISTIC:
            return gt.RvH
        elif white_type == pt.HEURISTIC and black_type == pt.HEURISTIC:
            return gt.HvH
        elif white_type == pt.RANDOM and black_type == pt.AI:
            return gt.RvAI
        elif white_type == pt.AI and black_type == pt.AI:
            return gt.AIvAI

    def get_game_winner(self):

        black_on_board = self.player2.get_number_of_pieces_on_board()
        white_on_board = self.player1.get_number_of_pieces_on_board()

        if black_on_board > white_on_board:
            print("Black wins!")
            return self.player2.get_team()
        elif white_on_board > black_on_board:
            print("White wins!")
            return self.player1.get_team()
        else:
            print("Tie game!")
            return None

    def agent_vs_agent_game(self):

        if self.current_turn == self.player1:
            agent_selected_move = self.agent_move_and_update(self.env_white)

            self.piece_to_move = agent_selected_move.get_start_position()
            self.piece_move_to = agent_selected_move.get_end_position()

        elif self.current_turn == self.player2:

            agent_selected_move = self.agent_move_and_update(self.env_black)

            self.piece_to_move = agent_selected_move.get_start_position()
            self.piece_move_to = agent_selected_move.get_end_position()

        if self.send_move_request():
            pass
        else:
            print("Agent move failed for " + str(self.current_turn))
            print(self.current_turn.printcurrentpieces())
            exit(1)

    def reset_game(self):
        self.board = checkboard(8, 8)
        self.board.setupdefaultboard()
        self.board.printboard()
        self.current_turn = random.choice([self.player1, self.player2])
        self.player1.init_player_vars()
        self.player2.init_player_vars()

    def new_random_vs_agent_game(self, outcome):
        self.reset_game()
        self.env_black.init_env_vars(self.board, self.player2)
        self.env_black.update_games_and_win_or_lose(outcome)

    def new_agent_vs_agent_game(self, outcome_black, outcome_white):
        self.reset_game()
        self.env_black.init_env_vars(self.board, self.player2)
        self.env_white.init_env_vars(self.board, self.player1)
        self.env_black.update_games_and_win_or_lose(outcome_black)
        self.env_white.update_games_and_win_or_lose(outcome_white)

    def random_vs_agent_game(self):

        if self.current_turn == self.player2:

            agent_selected_move = self.agent_move_and_update(self.env_black)

            self.piece_to_move = agent_selected_move.get_start_position()
            self.piece_move_to = agent_selected_move.get_end_position()

            self.player2.printcurrentpieces()
            if self.send_move_request():
                pass
            else:
                self.player2.printcurrentpieces()
                print(agent_selected_move)
                exit("AI failed a move.")

        elif self.current_turn == self.player1:
            self.get_random_move()
            self.send_move_request()


    def send_move_request(self):

        move_request = move(self.piece_to_move, self.piece_move_to, self.current_turn, 1, 1)

        print("Attemping: " + str(move_request))
        if move_request.makemove(self.board):
            self.update_game_after_move()
            return True
        else:
            print("Move failed")
            return False

    def agent_move_and_update(self, env):

        agent_move = env.calculate_best_move()
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
