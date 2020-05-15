from Checkers.CheckerBoard import CheckerBoard as checkboard
from Checkers.Player import Player as player
from Checkers.Player import RandomPlayer as randplayer
from Checkers.Move import Move as move
from Checkers.Enums import Player_Types as pt
from Checkers.Enums import Outcome as oc
from Checkers.Enums import Game_Type as gt
from Checkers.Enums import Team
from Checkers_Agent.checkers_env import CheckersEnv as env
from sys import exit
import random


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
        self.game_type = self._get_game_type()

    def run(self):
        self.board.setupdefaultboard()

        self.current_turn = random.choice([self.player1, self.player2])

        while 1:

            if self._check_terminal_state() is not None:
                winner = self._check_terminal_state()

                print("The winner is " + str(winner))

                self._resolve_end_game_state_and_setup_next_game(self.game_type, winner)

                self._exit_game_after_X_games()

            print(str(self.current_turn) + " turn: \n")

            if self.game_type == gt.PvP:
                self._take_player_input()
                # Turn coords into keys
                self._player_vs_player_loop()

            elif self.game_type == gt.RvR:
                self._get_random_move()
                self._send_move_request()

            elif self.game_type == gt.RvH:
                if self.init_agent:
                    self.env_black.init_env_vars(self.board, self.player2)
                    self.init_agent = False

                self._random_vs_agent_game()

            elif self.game_type == gt.HvH:
                if self.init_agent:
                    self.env_white.init_env_vars(self.board, self.player1)
                    self.env_black.init_env_vars(self.board, self.player2)
                    self.init_agent = False

                self._agent_vs_agent_game()

            elif self.game_type == gt.RvAI:
                if self.init_agent:
                    self.env_black.init_env_vars(self.board, self.player2)
                    self.init_agent = False

                self._random_vs_agent_game()

            elif self.game_type == gt.HvAI:
                if self.init_agent:
                    self.env_white.init_env_vars(self.board, self.player1)
                    self.env_black.init_env_vars(self.board, self.player2)
                    self.init_agent = False

                self._agent_vs_agent_game()

            elif self.game_type == gt.AIvAI:
                if self.init_agent:
                    self.env_white.init_env_vars(self.board, self.player1)
                    self.env_black.init_env_vars(self.board, self.player2)
                    self.init_agent = False

                self._agent_vs_agent_game()

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

    def _exit_game_after_X_games(self):

        if self.player2.get_games_played() == 200000:
            self.env_black.Env_Metrics.muppy_object_summary()
            exit("200k games played")

    def _resolve_end_game_state_and_setup_next_game(self, type, winner):

        if type == gt.RvH or type == gt.RvAI:
            if winner == Team.BLACK:
                self._new_random_vs_heuristic_game(oc.WIN)
                self.env_black.post_game_heuristics(oc.WIN)
            elif winner == Team.WHITE:
                self._new_random_vs_heuristic_game(oc.LOSE)
                self.env_black.post_game_heuristics(oc.LOSE)
            else:
                self._new_random_vs_heuristic_game(oc.TIE)
                self.env_black.post_game_heuristics(oc.TIE)

        elif type == gt.HvH or type == gt.AIvAI or type == gt.HvAI:
            if winner == Team.BLACK:
                self._new_agent_vs_agent_game(oc.WIN, oc.LOSE)
                self.env_black.post_game_heuristics(oc.WIN)
                self.env_white.post_game_heuristics(oc.LOSE)
            elif winner == Team.WHITE:
                self._new_agent_vs_agent_game(oc.LOSE, oc.WIN)
                self.env_black.post_game_heuristics(oc.LOSE)
                self.env_white.post_game_heuristics(oc.WIN)
            else:
                self._new_agent_vs_agent_game(oc.TIE, oc.TIE)
                self.env_black.post_game_heuristics(oc.TIE)
                self.env_white.post_game_heuristics(oc.TIE)

    def _get_game_type(self):

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
        elif white_type == pt.HEURISTIC and black_type == pt.AI:
            return gt.HvAI

    def _get_game_winner(self):

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

    def _agent_vs_agent_game(self):

        if self.current_turn == self.player1:

            agent_selected_move = self._agent_move_and_update(self.env_white)

            self.piece_to_move = agent_selected_move.get_start_position()
            self.piece_move_to = agent_selected_move.get_end_position()

            num_enemy_pieces = self.player1.get_number_of_pieces_on_board()
            if self._send_move_request():
                if self.player1.get_number_of_pieces_on_board() < num_enemy_pieces:
                    agent_selected_move.set_took_piece()
                pass
            else:
                print("Agent move failed for " + str(self.current_turn))
                print(self.current_turn.printcurrentpieces())
                exit(1)

        elif self.current_turn == self.player2:

            agent_selected_move = self._agent_move_and_update(self.env_black)

            self.piece_to_move = agent_selected_move.get_start_position()
            self.piece_move_to = agent_selected_move.get_end_position()

            num_enemy_pieces = self.player1.get_number_of_pieces_on_board()

            if self._send_move_request():
                if self.player1.get_number_of_pieces_on_board() < num_enemy_pieces:
                    agent_selected_move.set_took_piece()
                pass
            else:
                print("Agent move failed for " + str(self.current_turn))
                print(self.current_turn.printcurrentpieces())
                exit(1)

    def _reset_game(self):
        self.board = checkboard(8, 8)
        self.board.setupdefaultboard()
        self.board.printboard()
        self.current_turn = random.choice([self.player1, self.player2])
        self.player1.init_player_vars()
        self.player2.init_player_vars()

    def _new_random_vs_heuristic_game(self, outcome):
        self._reset_game()
        self.env_black.init_env_vars(self.board, self.player2)
        self.env_black.update_games_and_win_or_lose(outcome)

    def _new_agent_vs_agent_game(self, outcome_black, outcome_white):
        self._reset_game()
        self.env_black.init_env_vars(self.board, self.player2)
        self.env_white.init_env_vars(self.board, self.player1)
        self.env_black.update_games_and_win_or_lose(outcome_black)
        self.env_white.update_games_and_win_or_lose(outcome_white)

    def _random_vs_agent_game(self):

        if self.current_turn == self.player2:

            agent_selected_move = self._agent_move_and_update(self.env_black)

            self.piece_to_move = agent_selected_move.get_start_position()
            self.piece_move_to = agent_selected_move.get_end_position()

            self.player2.printcurrentpieces()

            num_enemy_pieces = self.player1.get_number_of_pieces_on_board()

            if self._send_move_request():
                if self.player1.get_number_of_pieces_on_board() < num_enemy_pieces:
                    agent_selected_move.set_took_piece()
                pass
            else:
                self.player2.printcurrentpieces()
                print(agent_selected_move)
                exit("AI failed a move.")

        elif self.current_turn == self.player1:
            self._get_random_move()
            self._send_move_request()

    def _send_move_request(self):

        move_request = move(self.piece_to_move, self.piece_move_to, self.current_turn, 1, 1)

        if move_request.make_move(self.board):
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

        if self.current_turn == self.player1:
            self.player2.remove_taken_piece(self.piece_move_to)
        else:
            self.player1.remove_taken_piece(self.piece_move_to)

    def _update_moveable_pieces(self):

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
                if isMoveable.make_move(self.board):
                    black_moveable_pieces.append(coord)
                    break
                else:
                    continue

        for coord in current_white_pieces_on_board:
            # (horizontalPos, verticalPos)
            for i in range(2):
                tempEndPosition = [a + b for a, b in zip(coord, deltaPositionsWhite[i])]
                isMoveable = move(coord, tempEndPosition, self.player1, 0)
                if isMoveable.make_move(self.board):
                    white_moveable_pieces.append(coord)
                    break
                else:
                    continue

        self.player1.update_moveable_pieces(white_moveable_pieces)
        self.player2.update_moveable_pieces(black_moveable_pieces)

    def _input_to_coordinates(self):

        self.piece_to_move = [int(s) for s in self.piece_to_move.split(',')]
        self.piece_move_to = [int(s) for s in self.piece_move_to.split(',')]

    def _get_random_move(self):

        self.piece_to_move = self.current_turn.choose_random_start_position()
        self.piece_move_to = self.current_turn.choose_random_end_position(self.piece_to_move.copy())

    def _check_if_exit(self):
        if self.piece_move_to.lower() == 'exit':
            exit(1)
        else:
            return

    def _update_current_turn(self):

        if self.current_turn == self.player1:
            self.current_turn = self.player2
        else:
            self.current_turn = self.player1

    def _check_terminal_state(self):

        if self.player1 is None or self.player2 is None:
            return None

        elif self.player1.get_number_of_current_moveable_pieces() == 0 and self.current_turn == self.player1:
            if self.game_type == gt.RvR or self._get_game_type() == gt.HvH:
                exit("Game over! Black wins!")

            else:
                return self.player2.get_team()

        elif self.player2.get_number_of_current_moveable_pieces() == 0 and self.current_turn == self.player2:
            if self.game_type == gt.RvR or self._get_game_type() == gt.HvH:
                exit("Game over! White wins!")

            else:
                return self.player1.get_team()

    def _take_player_input(self):
        self.piece_to_move = input("Piece to move? Format: x, y ")
        self.piece_move_to = input("Move to where? Format: x, y \n'exit' to exit: ")

    def _update_game_after_move(self):
        self._update_current_pieces_for_non_turn_player()
        self.board.printboard()
        self._update_moveable_pieces()
        self._update_current_turn()
        print("\n")
