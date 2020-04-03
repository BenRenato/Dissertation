from Checkers.Game import Game
import cProfile
import gym
import gym.envs
import gym_checkers
#TODO REINSTALL CUSTOM ENV WHEN CHANGING CHECKERSENV FUNCS

#TODO Standardise variable casing to Pythonic convention
#TODO Replace direct class memeber access with setters/getters
#TODO ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

def main():

    #TODO Make into method
    choice = int(input("Which game type?\n" +
          "1. Player vs Player\n" +
              "2. Random CPU vs Random CPU\n" +
                       "3. Player vs Random CPU\n" +
                       "4. Human vs AI agent\n"))

    if choice == 1:
        game = Game("human", "human")
        game.run()

    if choice == 2:
        game = Game("random", "random")
        game.run()

    if choice == 3:
        game = Game("human", "random")
        game.run()

    if choice == 4:

        env = gym.make('checkers-v0')
        env.step(print("Env stepping"))
        env.reset()
        

if __name__ == "__main__":

    main()

    #cProfile.run('main()')
