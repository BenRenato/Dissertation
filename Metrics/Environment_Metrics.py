import psutil
import os
from time import sleep
import numpy as np
from pympler import muppy, summary
import gc

# This class is responsible for recording the software metrics, and memory management, as well as
# writing environment data to a text file.

class EnvMetrics:
    def __init__(self):
        self.cull_data = True

    #----I/O TO TEXT FILE METHODS----#
    def write_env_data_to_file(self, WR, WR_10, game, team, state_space):

        ram_usage = self.get_ram_footprint()

        with open("env_data.txt", "a") as text_file:
            text_file.write("Game {} - WR for {} player (all/10 games): {:.2f}%/{:.2f}%\n"
                            "RAM usage: {}MB State space items: {}\n".format(game, team, WR, WR_10, ram_usage,
                                                                             state_space))

    def delete_previous_data(self):
        if os.path.exists("env_data.txt"):
            print("Previous env data found, deleting...")

            os.remove("env_data.txt")

            sleep(1)

        else:
            pass

    def cull_cached_state_space(self, state_space):
        print("Getting first quartile...")

        quartile = self._get_first_quartile_of_state_values(state_space)

        print("Deleting values below 1Q...")

        if self._delete_states_below_first_quartile(quartile, state_space) and self.cull_data:
            gc.collect()

            print("successfully culled data.")

            self.cull_data = False

            return True

        else:
            self.cull_data = True

            return False

    #----MEMORY MANAGEMENT METHODS----#
    def _muppy_object_summary(self):
        all_objects = muppy.get_objects()
        sum1 = summary.summarize(all_objects)
        summary.print_(sum1)
        sleep(5)

    def get_ram_footprint(self):
        process = psutil.Process(os.getpid())

        footprint = process.memory_info().rss / 1024 / 1024

        print("RAM footprint is: " + str(footprint) + " MB")

        return footprint

    def _get_first_quartile_of_state_values(self, state_space):
        value_space = self._build_list_of_state_values(state_space)

        first_quartile = np.percentile(value_space, 25)

        return first_quartile

    def _delete_states_below_first_quartile(self, quartile, state_space):

        for state_action_pair in state_space[:]:
            if state_action_pair.get_action_pair().get_value() < quartile:
                state_space.remove(state_action_pair)

                print("GC removing...")

            else:
                print("passing deletion, value higher...")

        print("Collecting left overs of delete_states_below_first_quartile...")

        return True

    def _build_list_of_state_values(self, state_space):
        list_of_state_values = []

        for state_action_value in state_space:
            list_of_state_values.append(state_action_value.get_action_pair().get_value())

        return list_of_state_values
