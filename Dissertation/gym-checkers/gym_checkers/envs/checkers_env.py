import gym
from gym import error, spaces, utils
from gym.utils import seeding

class CheckersEnv(gym.Env):
  metadata = {'render.modes': ['human', 'terminal']}



  def __init__(self):
    print("Gym init")
  def step(self, action):
    print("Gym step")
  def reset(self):
    print("Gym reset")
  def render(self, mode='human', close=False):
    print("Gym render")
