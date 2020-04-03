from gym.envs.registration import register

register(
    id='checkers-v0',
    entry_point='gym_checkers.envs:CheckersEnv',
)
