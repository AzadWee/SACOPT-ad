import gym
import numpy as np
from gym.spaces import Box, Discrete
from tianshou.env import DummyVectorEnv
from .manager import Manager
from .config import *


class OPTEnv(gym.Env):

    def __init__(self):
        self._manager = Manager()
        self._observation_space = Box(shape=self.state.shape, low=0, high=1)

        vehicle_id_space = Discrete(GOOD_VEHICLE_NUMBER + BED_VEHICLE_NUMBER)
        # block_size_space = Box(low=MIN_BLOCK_SIZE, high=MAX_BLOCK_SIZE, shape=(1,), dtype=float)
        # block_interval_space = Box(low=MIN_BLOCK_INTERVAL, high=MAX_BLOCK_INTERVAL, shape=(1,), dtype=float)

        self._action_space = vehicle_id_space

        self._num_steps = 0
        self.global_step = 0
        self._done = 0

    @property
    def state(self):
        return self._manager.space_vector

    @property
    def observation_space(self):
        return self._observation_space

    @property
    def action_space(self):
        return self._action_space

    @property
    def manager(self):
        return self._manager

    def step(self, action):
        assert not self._done, "One episodic has terminated"
        # print('action:', action)
        reward = self._manager.set(action, self.global_step)
        self._num_steps += 1
        self.global_step += 1
        if self._num_steps >= MAX_STEP:
            self._done = 1
        info = {'num_steps': self._num_steps}
        return self.state, reward, self._done, info

    def reset(self):
        self._manager.reset()
        self._num_steps = 0
        self._done = 0
        return self.state

    def seed(self, seed=None):
        np.random.seed(seed)


def make_env(training_num=0, test_num=0):
    env = OPTEnv()
    env.seed(SEED)
    train_envs, test_envs = None, None
    if training_num:
        train_envs = DummyVectorEnv([lambda:OPTEnv() for _ in range(training_num)])
        train_envs.seed(SEED)

    if test_num:
        test_envs = DummyVectorEnv([lambda:OPTEnv() for _ in range(test_num)])
        test_envs.seed(SEED)

    return env, train_envs, test_envs
