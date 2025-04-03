import gym
import numpy as np
import csv
import os
from gym.spaces import Box, Discrete
from tianshou.env import DummyVectorEnv
from .manager import Manager
from .config import *


class OPTEnv(gym.Env):

    def __init__(self, is_save):
        self._manager = Manager()
        self._observation_space = Box(shape=self.state.shape, low=0, high=1)

        # block_size_space = Box(low=MIN_BLOCK_SIZE, high=MAX_BLOCK_SIZE, shape=(1,), dtype=float)
        # block_interval_space = Box(low=MIN_BLOCK_INTERVAL, high=MAX_BLOCK_INTERVAL, shape=(1,), dtype=float)

        self._action_space = Discrete(ACTION_SPACE)
        self.is_save = is_save
        self._num_steps = 0
        self.global_clock = 0
        self._done = 0
        self.throughput_records = []
        self.plenty_records = []
        self.delay_records = []
        self.data_size_records = []
        self.bad_count_record = 0

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
        reward, manage_info = self._manager.set(action, self.global_clock)
        self.throughput_records.append(manage_info['throughput'])
        self.delay_records.append(manage_info['delay'])
        self.plenty_records.append(manage_info['plenty'])
        self.data_size_records.append(manage_info['data_size'])
        self.bad_count_record = manage_info['bad_count']
        
        self._num_steps += 1
        self.global_clock += 1
        if self._num_steps >= MAX_STEP:
            self._done = 1
        info = {'num_steps': self._num_steps, 'throughput': manage_info['throughput']}
        return self.state, reward, self._done, info

    def reset(self):
        self._manager.reset()
        self._num_steps = 0
        self._done = 0
        if self.is_save:
            self.save_to_csv()
        self.throughput_records = []
        self.plenty_records = []
        self.delay_records = []
        self.data_size_records = []
        self.bad_count_record = 0
        return self.state

    def seed(self, seed=None):
        np.random.seed(seed)

    def save_to_csv(self, filename='records.csv'):
        file_exists = os.path.isfile(filename)
        mean_throughput = 0
        mean_plenty = 0
        with open(filename, mode='a+', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['throughput', 'delay', 'plenty', 'data_size', 'bad_count'])
            if self.throughput_records:
                mean_throughput = sum(self.throughput_records) / len(self.throughput_records)
            if self.plenty_records:
                mean_plenty = sum(self.plenty_records) / len(self.plenty_records)
            if self.delay_records:
                mean_delay = sum(self.delay_records) / len(self.delay_records)
            if self.data_size_records:
                mean_data_size = sum(self.data_size_records) / len(self.data_size_records)
            
            if mean_throughput:
                writer.writerow([mean_throughput, mean_delay, mean_plenty, mean_data_size, self.bad_count_record])


def make_env(training_num=0, test_num=0, save=False):
    env = OPTEnv(save)
    env.seed(SEED)
    train_envs, test_envs = None, None
    if training_num:
        train_envs = DummyVectorEnv([lambda:OPTEnv(save) for _ in range(training_num)])
        train_envs.seed(SEED)

    if test_num:
        test_envs = DummyVectorEnv([lambda:OPTEnv(save) for _ in range(test_num)])
        test_envs.seed(SEED)

    return env, train_envs, test_envs
