from Checkers.Game import Game
from Checkers.Enums import Player_Types as pt
import cProfile

#TODO REINSTALL CUSTOM ENV WHEN CHANGING CHECKERSENV FUNCS

#TODO Standardise variable casing to Pythonic convention
#TODO Replace direct class memeber access with setters/getters
#TODO ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

def main():

    #TODO Make into method
    choice = int(input("Which game type?\n" +
          "1. Player vs Player\n" +
              "2. Random CPU vs Random CPU\n" +
                       "3. Random vs AI agent\n"))

    if choice == 1:
        game = Game(pt.HUMAN, pt.HUMAN)
        game.run()

    if choice == 2:
        game = Game(pt.RANDOM, pt.RANDOM)
        game.run()

    if choice == 3:

        game = Game(pt.RANDOM, pt.AI)
        game.run()
        

if __name__ == "__main__":

    main()

    #cProfile.run('main()')
