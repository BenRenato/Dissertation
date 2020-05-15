from Checkers.CheckerBoard import CheckerBoard as checkboard
from Checkers.Player import Player as player
from Checkers.Player import RandomPlayer as randplayer
from Checkers.Move import Move as move
from Checkers.Enums import Player_Types as pt
from Checkers.Enums import Outcome as oc
from Checkers.Enums import Game_Type as gt
from Checkers.Enums import Team
from Checkers_Agent.Checkers_Env import CheckersEnv as env
from sys import exit
import random


# This class handles all logic for running the game loop.
# The class also has methods that relate to checking terminal games states, updating player pieces, and
# deciding how to proceed with new games after a single agent game has been completed.

class Game:

    def __init__(self, player1_type, player2_type):

        self._board = checkboard(8, 8)

        # Player 1
        if player1_type == pt.HUMAN:
            self._player1 = player(False, pt.HUMAN)

        elif player1_type == pt.HEURISTIC:
            self._player1 = player(False, pt.HEURISTIC)

            self._env_white = env()

        elif player1_type == pt.RANDOM:
            self._player1 = randplayer(False, pt.RANDOM)

        elif player1_type == pt.AI:
            self._player1 = player(False, pt.AI)

            self._env_white = env(False)

        # Player 2
        if player2_type == pt.HUMAN:
            self._player2 = player(True, pt.HUMAN)

        elif player2_type == pt.HEURISTIC:
            self._player2 = player(True, pt.HEURISTIC)

            self._env_black = env()

        elif player2_type == pt.RANDOM:
            self._player2 = randplayer(True, pt.RANDOM)

        elif player2_type == pt.AI:
            self._player2 = player(True, pt.AI)

            self._env_black = env(False)

        self._piece_to_move = None
        self._piece_move_to = None

        self._current_turn = None

        self._init_agent = True

        self._game_type = self._get_game_type()

    # -------------------PUBLIC METHODS-------------------#
    def run(self):
        self._board.setupdefaultboard()

        self._current_turn = random.choice([self._player1, self._player2])

        while 1:

            if self._check_terminal_state() is not None:
                winner = self._check_terminal_state()

                print("The winner is " + str(winner))

                self._resolve_end_game_state_and_setup_next_game(self._game_type, winner)

                self._exit_game_after_X_games()

            print(str(self._current_turn) + " turn: \n")

            # Proceed with checking game type and proceed with the correct functionality
            if self._game_type == gt.PvP:
                self._take_player_input()
                # Turn coords into keys
                self._player_vs_player_loop()

            elif self._game_type == gt.RvR:
                self._get_random_move()

                self._send_move_request()

            elif self._game_type == gt.RvH:
                if self._init_agent:

                    self._env_black.init_env_vars(self._board, self._player2)

                    self._init_agent = False

                self._random_vs_agent_game()

            elif self._game_type == gt.HvH:
                if self._init_agent:
                    self._env_white.init_env_vars(self._board, self._player1)

                    self._env_black.init_env_vars(self._board, self._player2)

                    self._init_agent = False

                self._agent_vs_agent_game()

            elif self._game_type == gt.RvAI:
                if self._init_agent:
                    self._env_black.init_env_vars(self._board, self._player2)

                    self._init_agent = False

                self._random_vs_agent_game()

            elif self._game_type == gt.HvAI:
                if self._init_agent:
                    self._env_white.init_env_vars(self._board, self._player1)

                    self._env_black.init_env_vars(self._board, self._player2)

                    self._init_agent = False

                self._agent_vs_agent_game()

            elif self._game_type == gt.AIvAI:
                if self._init_agent:
                    self._env_white.init_env_vars(self._board, self._player1)

                    self._env_black.init_env_vars(self._board, self._player2)

                    self._init_agent = False

                self._agent_vs_agent_game()

    # -------------------PRIVATE METHODS-------------------#

    #----GAME LOOPS----#
    def _player_vs_player_loop(self):
        while True:
            try:
                self._check_if_exit()

                self._input_to_coordinates()

                self._send_move_request()
            except ValueError:
                print("Wrong format")

                self._take_player_input()

                continue

            else:
                break

    def _agent_vs_agent_game(self):
        if self._current_turn == self._player1:

            agent_selected_move = self._agent_move_and_update(self._env_white)

            self._piece_to_move = agent_selected_move.get_start_position()
            self._piece_move_to = agent_selected_move.get_end_position()

            num_enemy_pieces = self._player1.get_number_of_pieces_on_board()

            if self._send_move_request():
                if self._player1.get_number_of_pieces_on_board() < num_enemy_pieces:
                    agent_selected_move.set_took_piece()

                pass

            else:
                print("Agent move failed for " + str(self._current_turn))

                exit(1)

        elif self._current_turn == self._player2:
            agent_selected_move = self._agent_move_and_update(self._env_black)

            self._piece_to_move = agent_selected_move.get_start_position()
            self._piece_move_to = agent_selected_move.get_end_position()

            num_enemy_pieces = self._player1.get_number_of_pieces_on_board()

            if self._send_move_request():
                if self._player1.get_number_of_pieces_on_board() < num_enemy_pieces:
                    agent_selected_move.set_took_piece()

                pass

            else:
                print("Agent move failed for " + str(self._current_turn))

                exit(1)

    def _random_vs_agent_game(self):
        if self._current_turn == self._player2:
            agent_selected_move = self._agent_move_and_update(self._env_black)

            self._piece_to_move = agent_selected_move.get_start_position()
            self._piece_move_to = agent_selected_move.get_end_position()

            num_enemy_pieces = self._player1.get_number_of_pieces_on_board()

            if self._send_move_request():
                if self._player1.get_number_of_pieces_on_board() < num_enemy_pieces:
                    agent_selected_move.set_took_piece()

                pass

            else:
                print(agent_selected_move)

                exit("AI failed a move.")

        elif self._current_turn == self._player1:
            self._get_random_move()

            self._send_move_request()

    def _update_current_turn(self):
        if self._current_turn == self._player1:
            self._current_turn = self._player2

        else:
            self._current_turn = self._player1

    #----RESET GAME AND START NEW METHODS----#
    def _check_terminal_state(self):
        if self._player1 is None or self._player2 is None:
            return None

        elif self._player1.get_number_of_current_moveable_pieces() == 0 and self._current_turn == self._player1:
            if self._game_type == gt.RvR or self._get_game_type() == gt.HvH:
                exit("Game over! Black wins!")

            else:
                return self._player2.get_team()

        elif self._player2.get_number_of_current_moveable_pieces() == 0 and self._current_turn == self._player2:
            if self._game_type == gt.RvR or self._get_game_type() == gt.HvH:
                exit("Game over! White wins!")

            else:
                return self._player1.get_team()

    def _check_if_exit(self):
        if self._piece_move_to.lower() == 'exit':
            exit(1)

        else:
            return

    def _exit_game_after_X_games(self):
        if self._player2.get_games_played() == 200000:
            exit("200k games played")

    def _resolve_end_game_state_and_setup_next_game(self, type, winner):
        if type == gt.RvH or type == gt.RvAI:
            if winner == Team.BLACK:
                self._new_random_vs_heuristic_game(oc.WIN)

                self._env_black.post_game_heuristics(oc.WIN)

            elif winner == Team.WHITE:
                self._new_random_vs_heuristic_game(oc.LOSE)

                self._env_black.post_game_heuristics(oc.LOSE)

            else:
                self._new_random_vs_heuristic_game(oc.TIE)

                self._env_black.post_game_heuristics(oc.TIE)

        elif type == gt.HvH or type == gt.AIvAI or type == gt.HvAI:
            if winner == Team.BLACK:
                self._new_agent_vs_agent_game(oc.WIN, oc.LOSE)

                self._env_black.post_game_heuristics(oc.WIN)
                self._env_white.post_game_heuristics(oc.LOSE)

            elif winner == Team.WHITE:
                self._new_agent_vs_agent_game(oc.LOSE, oc.WIN)

                self._env_black.post_game_heuristics(oc.LOSE)
                self._env_white.post_game_heuristics(oc.WIN)

            else:
                self._new_agent_vs_agent_game(oc.TIE, oc.TIE)

                self._env_black.post_game_heuristics(oc.TIE)
                self._env_white.post_game_heuristics(oc.TIE)

    def _reset_game(self):
        self._board = checkboard(8, 8)

        self._board.setupdefaultboard()
        self._board.printboard()

        self._current_turn = random.choice([self._player1, self._player2])

        self._player1.init_player_vars()
        self._player2.init_player_vars()

    def _new_random_vs_heuristic_game(self, outcome):
        self._reset_game()

        self._env_black.init_env_vars(self._board, self._player2)

        self._env_black.update_games_and_win_or_lose(outcome)

    def _new_agent_vs_agent_game(self, outcome_black, outcome_white):
        self._reset_game()

        self._env_black.init_env_vars(self._board, self._player2)
        self._env_white.init_env_vars(self._board, self._player1)

        self._env_black.update_games_and_win_or_lose(outcome_black)
        self._env_white.update_games_and_win_or_lose(outcome_white)

    #----MOVE METHODS----#
    def _update_game_after_move(self):
        self._update_current_pieces_for_non_turn_player()

        self._board.printboard()

        self._update_moveable_pieces()

        self._update_current_turn()

        print("\n")

    def _send_move_request(self):
        move_request = move(self._piece_to_move, self._piece_move_to, self._current_turn, 1, 1)

        if move_request.make_move(self._board):
            self._update_game_after_move()

            return True

        else:
            print("Move failed")

            return False

    def _agent_move_and_update(self, env):
        agent_move = env.calculate_best_move()

        agent_move.set_update_pieces_value(1)

        return agent_move

    def _update_current_pieces_for_non_turn_player(self):
        if self._current_turn == self._player1:
            self._player2.remove_taken_piece(self._piece_move_to)

        else:
            self._player1.remove_taken_piece(self._piece_move_to)

    def _update_moveable_pieces(self):
        current_black_pieces_on_board = self._player2.get_current_pieces()  # player 2 is black
        current_white_pieces_on_board = self._player1.get_current_pieces()  # player 1 is white

        black_moveable_pieces = []
        white_moveable_pieces = []

        deltaPositionsBlack = [[-1, -1], [1, -1]]
        deltaPositionsWhite = [[-1, 1], [1, 1]]

        for coord in current_black_pieces_on_board:
            # (horizontalPos, verticalPos)
            for i in range(2):
                tempEndPosition = [a + b for a, b in zip(coord, deltaPositionsBlack[i])]

                isMoveable = move(coord, tempEndPosition, self._player2, 0)

                if isMoveable.make_move(self._board):
                    black_moveable_pieces.append(coord)

                    break

                else:
                    continue

        for coord in current_white_pieces_on_board:
            # (horizontalPos, verticalPos)
            for i in range(2):
                tempEndPosition = [a + b for a, b in zip(coord, deltaPositionsWhite[i])]

                isMoveable = move(coord, tempEndPosition, self._player1, 0)

                if isMoveable.make_move(self._board):
                    white_moveable_pieces.append(coord)

                    break

                else:
                    continue

        self._player1.update_moveable_pieces(white_moveable_pieces)
        self._player2.update_moveable_pieces(black_moveable_pieces)

    def _get_random_move(self):
        self._piece_to_move = self._current_turn.choose_random_start_position()
        self._piece_move_to = self._current_turn.choose_random_end_position(self._piece_to_move.copy())

    #----INPUT----#
    def _take_player_input(self):
        self._piece_to_move = input("Piece to move? Format: x, y ")

        self._piece_move_to = input("Move to where? Format: x, y \n'exit' to exit: ")

    def _input_to_coordinates(self):
        self._piece_to_move = [int(s) for s in self._piece_to_move.split(',')]

        self._piece_move_to = [int(s) for s in self._piece_move_to.split(',')]

    #----GETTERS AND SETTERS----#
    def _get_game_type(self):
        white_type = self._player1.get_player_type()
        black_type = self._player2.get_player_type()

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

        elif white_type == pt.HEURISTIC and black_type == pt.AI:
            return gt.HvAI

    def _get_game_winner(self):
        black_on_board = self._player2.get_number_of_pieces_on_board()
        white_on_board = self._player1.get_number_of_pieces_on_board()

        if black_on_board > white_on_board:
            print("Black wins!")

            return self._player2.get_team()

        elif white_on_board > black_on_board:
            print("White wins!")

            return self._player1.get_team()

        else:
            print("Tie game!")

            return None