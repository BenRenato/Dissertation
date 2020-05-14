from Checkers.Enums import Team, Direction, Player_Types

class Move:

    def __init__(self, startposition, endposition, player, update=0, update_pieces=0):
        self.update_pieces = update_pieces
        self.startposition = startposition
        self.endposition = endposition
        self.player = player
        self.updatenow = update
        self.took_enemy_piece = False

    def set_took_piece(self):
        self.took_enemy_piece = True

    def get_took_enemy_piece(self):
        return self.took_enemy_piece

    def makemove(self, boardstate):

        board = boardstate

        if not self.check_positions_are_valid(board, self.startposition, self.endposition):
            return False

        if self.validatemove(board):
            #print("Valid move")
            if self.updatenow == 1:
                self.updatepiece(board, self.startposition, self.endposition)
                if self.update_pieces == 1:
                    self.player.updatecurrentpieces(self.startposition, self.endposition)
            return True
        else:
            #print("Invalid move")
            return False

    def validatemove(self, board):

        if self.validate_movement_correct():
            if board[self.endposition].getoccupier().team == Team.EMPTY:
                return True
            elif board[self.endposition].getoccupier().team != self.player.get_team():
                #print("Validating taking move")
                if self.validate_taking_move(board):
                    return True
                else:
                    return False
            else:
                #print("Cannot take same team piece")
                return False


    def validate_taking_move(self, board):

        direction_horizontal = self.get_horizontal_direction()
        direction_vertical = self.get_vertical_direction()

        #This is not readable but FASTEST way to copy lists without reference, same as list.copy()
        end_position_of_jump = self.endposition[:]

        #TODO method-ify this
        if direction_vertical == Direction.UP:
            end_position_of_jump[1] -= 1
        elif direction_vertical == Direction.DOWN:
            end_position_of_jump[1] += 1
        if direction_horizontal == Direction.LEFT:
            end_position_of_jump[0] -= 1
        elif direction_horizontal == Direction.RIGHT:
            end_position_of_jump[0] += 1

        if not self.check_position_out_of_bounds(end_position_of_jump):
            return False

        if board[end_position_of_jump].getoccupier().team == Team.EMPTY:
            if self.updatenow == 1:
                if self.update_pieces == 1:
                    #print("Updating taken piece")
                    self.removepiece(board, self.endposition)
                if self.player.get_player_type() != Player_Types.HEURISTIC and self.player.get_player_type() != Player_Types.AI:
                    self.endposition = end_position_of_jump
                else:
                    pass

            #TODO update amount of pieces Player class captured here
            #self.player.update_captured_pieces(1) to increase count by 1
            return True
        else:
            return False

    def check_position_out_of_bounds(self, position):

        try:
            x, y = position

        #TODO specifiy Exception cases
        except Exception:
            return False

        # Cannot move off board
        if x >= 8 or x < 0 or y >= 8 or y < 0:
            return False
        else:
            return True

    def get_vertical_direction(self):

        if self.player.isblack:
            return Direction.UP
        else:
            return Direction.DOWN

    def get_horizontal_direction(self):

        if self.startposition[0] - self.endposition[0] == 1:
            return Direction.LEFT
        else:
            return Direction.RIGHT

    def validate_movement_correct(self):
        # Move in correct direction
        if self.player.isblack:
            #print(self.startposition, self.endposition)
            if abs(self.startposition[0] - self.endposition[0]) != 1 \
                    or (self.startposition[1] - self.endposition[1]) != 1:
                return False
            else:
                return True

        else:
            #print(self.startposition, self.endposition)
            if abs(self.startposition[0] - self.endposition[0]) != 1 \
                    or (self.startposition[1] - self.endposition[1]) != -1:
                return False
            else:
                return True

    def removepiece(self, board, key):

        x, y = key

        board[x, y].updateoccupier("empty", "empty")

    def updatepiece(self, board, movefrom, moveto):

        a, b = movefrom
        x, y = moveto

        startpiece = board[a, b].getoccupier()

        board[x, y].updateoccupier(startpiece.team, startpiece.rank)

        self.removepiece(board, movefrom)

    def check_positions_are_valid(self, board, start, end):

        if not self.check_position_out_of_bounds(start) or not self.check_position_out_of_bounds(end):
            return False

        if board[self.startposition].getoccupier().team == Team.EMPTY:
            print("Specificed piece doesn't exist")
            return False
        else:
            return True

    def get_start_position(self):
        return self.startposition

    def get_end_position(self):
        return self.endposition

    def set_update_pieces_value(self, update_pieces):
        self.update_pieces = update_pieces

    def __repr__(self):
        return "Positions " + str(self.startposition + self.endposition)