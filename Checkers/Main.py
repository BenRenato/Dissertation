from Checkers.Game import Game
from Checkers.Enums import Player_Types as pt
import cProfile

def main():

    choice = int(input("Which game type?\n" +
                       "1. Player vs Player\n" +
                       "2. Random CPU vs Random CPU\n" +
                       "3. Random CPU vs Heuristic agent (black)\n" +
                       "4. Heuristic agent vs Heuristic agent\n" +
                       "5. Random CPU vs RL agent\n" +
                       "6. RL agent vs RL agent\n" +
                       "7. Heuristic vs RL agent\n"))

    if choice == 1:
        game = Game(pt.HUMAN, pt.HUMAN)

        game.run()

    elif choice == 2:
        game = Game(pt.RANDOM, pt.RANDOM)

        game.run()

    elif choice == 3:
        game = Game(pt.RANDOM, pt.HEURISTIC)

        game.run()

    elif choice == 4:
        game = Game(pt.HEURISTIC, pt.HEURISTIC)

        game.run()

    elif choice == 5:
        game = Game(pt.RANDOM, pt.AI)

        game.run()

    elif choice == 6:
        game = Game(pt.AI, pt.AI)

        game.run()

    elif choice == 7:
        game = Game(pt.HEURISTIC, pt.AI)

        game.run()


if __name__ == "__main__":
    main()

    #cProfile.run('main()')
