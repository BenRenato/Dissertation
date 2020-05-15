from Checkers.Enums import Team, Direction, Player_Types

class Move:

    def __init__(self, start_position, end_position, player, update=0, update_pieces=0):
        self._start_position = start_position
        self._end_position = end_position

        self.player = player

        self._update_pieces = update_pieces
        self._update_now = update

        self._took_enemy_piece = False

    #----CLASS ATTRIBUTE METHODS----#
    def __repr__(self):
        return "Positions " + str(self._start_position + self._end_position)

    #----MOVE METHOD LOGIC----#
    def make_move(self, board_state):

        board = board_state

        if not self._check_positions_are_valid(board, self._start_position, self._end_position):
            return False

        if self._validate_move(board):
            if self._update_now == 1:
                self._update_piece(board, self._start_position, self._end_position)

                if self._update_pieces == 1:
                    self.player._update_current_pieces(self._start_position, self._end_position)

            return True

        else:
            return False

    def _validate_move(self, board):

        if self._validate_movement_correct():
            if board[self._end_position].get_occupier().get_team() == Team.EMPTY:
                return True

            elif board[self._end_position].get_occupier().get_team() != self.player.get_team():
                if self._validate_taking_move(board):

                    return True

                else:
                    return False
            else:
                return False

    def _validate_taking_move(self, board):

        direction_horizontal = self._get_horizontal_direction()
        direction_vertical = self._get_vertical_direction()

        #This is not readable but FASTEST way to copy lists without reference, same as list.copy()
        end_position_of_jump = self._end_position[:]

        if direction_vertical == Direction.UP:
            end_position_of_jump[1] -= 1

        elif direction_vertical == Direction.DOWN:
            end_position_of_jump[1] += 1

        if direction_horizontal == Direction.LEFT:
            end_position_of_jump[0] -= 1

        elif direction_horizontal == Direction.RIGHT:
            end_position_of_jump[0] += 1

        if not self._check_position_out_of_bounds(end_position_of_jump):
            return False

        if board[end_position_of_jump].get_occupier().get_team() == Team.EMPTY:
            if self._update_now == 1:
                if self._update_pieces == 1:
                    self._remove_piece(board, self._end_position)

                if self.player.get_player_type() != Player_Types.HEURISTIC and self.player.get_player_type() != Player_Types.AI:
                    self._end_position = end_position_of_jump

                else:
                    pass

            return True
        else:
            return False

    def _validate_movement_correct(self):
        # Move in correct direction
        if self.player.get_team() == Team.BLACK:
            if abs(self._start_position[0] - self._end_position[0]) != 1 \
                    or (self._start_position[1] - self._end_position[1]) != 1:
                return False

            else:
                return True

        else:
            if abs(self._start_position[0] - self._end_position[0]) != 1 \
                    or (self._start_position[1] - self._end_position[1]) != -1:
                return False

            else:
                return True

    #----MOVE POSITIONAL CHECKS----#
    def _check_position_out_of_bounds(self, position):
        try:
            x, y = position

        except Exception:
            return False

        # Cannot move off board
        if x >= 8 or x < 0 or y >= 8 or y < 0:
            return False

        else:
            return True

    def _check_positions_are_valid(self, board, start, end):

        if not self._check_position_out_of_bounds(start) or not self._check_position_out_of_bounds(end):
            return False

        if board[self._start_position].get_occupier().get_team() == Team.EMPTY:
            print("Specificed piece doesn't exist")
            return False

        else:
            return True

    #----BOARD UPDATES----#
    def _remove_piece(self, board, key):

        x, y = key

        board[x, y].update_occupier("empty", "empty")

    def _update_piece(self, board, move_from, move_to):

        a, b = move_from
        x, y = move_to

        start_piece = board[a, b].get_occupier()

        board[x, y].update_occupier(start_piece.get_team(), start_piece.get_rank())

        self._remove_piece(board, move_from)

    #----SETTERS AND GETTERS----#
    def get_start_position(self):
        return self._start_position

    def get_end_position(self):
        return self._end_position

    def set_update_pieces_value(self, update_pieces):
        self._update_pieces = update_pieces

    def _get_vertical_direction(self):

        if self.player.get_team() == Team.BLACK:
            return Direction.UP
        else:
            return Direction.DOWN

    def _get_horizontal_direction(self):

        if self._start_position[0] - self._end_position[0] == 1:
            return Direction.LEFT

        else:
            return Direction.RIGHT

    def set_took_piece(self):
        self._took_enemy_piece = True

    def get_took_enemy_piece(self):
        return self._took_enemy_piece