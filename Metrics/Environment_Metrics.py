import psutil
import os
from time import sleep



class Env_Metrics:

    def __init__(self):
        pass

    def write_env_data_to_file(self, WR, WR_10, game, team):
        # TODO also write best, worst, and average values to file
        # TODO also method the path exists stuff keep write logic

        RAM_usage = self.get_RAM_footprint()

        with open("env_data.txt", "a") as text_file:
            text_file.write("Game {} - WR for {} player (all/10 games): {:.2f}%/{:.2f}%\n"
                            "RAM usage: {}MB\n".format(game, team, WR, WR_10, RAM_usage))

    def cull_cached_state_space(self, state_space):
        # TODO iterate and cull
        pass

    def get_RAM_footprint(self):
        process = psutil.Process(os.getpid())
        footprint = process.memory_info().rss / 1024 / 1024
        print("RAM footprint is: " + str(footprint) + " MB")

        return footprint

    def delete_previous_data(self):
        if os.path.exists("env_data.txt"):
            print("Previous env data found, deleting...")
            os.remove("env_data.txt")
            sleep(5)
        else:
            pass