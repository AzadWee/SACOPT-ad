import numpy as np
from .config import *
from .block import Block


class Transaction:
    def __init__(self, vid, is_fake=0, size=1):
        self.vid = vid
        self.is_fake = is_fake
        self.size = size


class Vehicle:
    def __init__(self, vid, rid):
        self.vid = vid
        self.rid = rid  # 车辆所属rsu
        self.is_fov = False    # 是否是头车
        self.capacity = 10  # 计算能力
        self.transrate = 20  # 到rsu传输速率
        self.block_chain = []
    
    @property
    def norm_capacity(self):
        return self.capacity / CAPACITY[-1]
    
    @property
    def norm_transrate(self):
        return self.transrate / TRANS_RATE[-1]
    
    @property
    def vector(self):
        return np.hstack([self.norm_capacity, self.norm_transrate])
    
    def set_fov(self, is_fov):
        self.is_fov = is_fov

    def change_capacity(self, capacity):
        self.capacity = capacity

    def change_transrate(self, transrate):
        self.transrate = transrate
    
    def generate_transaction(self,t_size, t_lamma, min_size, max_size):
        random_number = np.random.normal(t_size, t_lamma)
        size = int(np.clip(random_number, min_size, max_size))

        trans = Transaction(vid=self.vid, is_fake=False, size=size)

        return trans
    
    def generate_block(self, block: Block):
        lantacy = block.size / self.capacity
        return lantacy

    def upload_block(self, block: Block):
        lantacy = block.size / self.transrate
        return lantacy

    def reset(self):
        self.is_fov = False
        self.block_chain.clear()
        self.capacity = np.random.choice(CAPACITY)  # 计算能力
        self.transrate = np.random.choice(TRANS_RATE)  # 到rsu传输速率
        self.reputation = 100  # 声誉
