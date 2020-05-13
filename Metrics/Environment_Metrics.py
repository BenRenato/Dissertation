import psutil
import os
from time import sleep
import numpy as np
from pympler import muppy, summary
import gc

class Env_Metrics:

    def __init__(self):
        pass

    def write_env_data_to_file(self, WR, WR_10, game, team):

        ram_usage = self.get_ram_footprint()

        with open("env_data.txt", "a") as text_file:
            text_file.write("Game {} - WR for {} player (all/10 games): {:.2f}%/{:.2f}%\n"
                            "RAM usage: {}MB\n".format(game, team, WR, WR_10, ram_usage))

    def cull_cached_state_space(self, state_space):

        quartile = self.get_first_quartile_of_state_values(state_space)
        if self.delete_states_below_first_quartile(quartile, state_space):
            print("successfully culled data.")
            gc.collect()
            return True
        else:
            return False

    def muppy_object_summary(self):
        all_objects = muppy.get_objects()
        sum1 = summary.summarize(all_objects)
        summary.print_(sum1)
        sleep(5)

    def get_ram_footprint(self):

        process = psutil.Process(os.getpid())
        footprint = process.memory_info().rss / 1024 / 1024
        print("RAM footprint is: " + str(footprint) + " MB")

        return footprint

    def delete_previous_data(self):

        if os.path.exists("env_data.txt"):
            print("Previous env data found, deleting...")
            os.remove("env_data.txt")
            sleep(2)
        else:
            pass

    def get_first_quartile_of_state_values(self, state_space):

        value_space = self.build_list_of_state_values(state_space)

        first_quartile = np.percentile(value_space, 25)

        return first_quartile

    def delete_states_below_first_quartile(self, quartile, state_space):

        for state_action_pair in state_space[:]:
            if state_action_pair.get_action_pair().get_value() < quartile:
                state_space.remove(state_action_pair)
            else:
                pass

        return True

    def build_list_of_state_values(self, state_space):

        list_of_state_values = []

        for state_action_value in state_space:
            list_of_state_values.append(state_action_value.get_action_pair().get_value())

        return list_of_state_values
