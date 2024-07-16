import random
from .config import *


class Transaction:
    def __init__(self, vid, is_fake=0, size=1):
        self.vid = vid
        self.is_fake = is_fake
        self.size = size


class Vehicle:
    def __init__(self, vid, is_bad, rid):
        self.vid = vid
        self.rid = rid  # 车辆所属rsu
        self.is_fov = False    # 是否是头车
        self.is_bad = is_bad   # 是否是恶意节点
        self.capacity = 10  # 计算能力
        self.transrate = 20  # 到rsu传输速率
        self.reputation = 100  # 声誉
        self.block_chain = []

    def set_fov(self, is_fov):
        self.is_fov = is_fov

    def change_capacity(self, capacity):
        self.capacity = capacity

    def change_transrate(self, transrate):
        self.transrate = transrate

    def generate_transaction(self):
        size = random.randint(MIN_TRANSACTION_SIZE, MAX_TRANSACTION_SIZE)

        if self.is_bad:
            if random.random() < 0.9:
                is_fake = True
            else:
                is_fake = False
        else:
            if random.random() <= 0.1:
                is_fake = True
            else:
                is_fake = False

        trans = Transaction(vid=self.vid, is_fake=is_fake, size=size)
        lantacy = size / self.capacity

        return trans, lantacy

    def add_block(self, block):
        self.block_chain.append(block)

    def reset(self):
        self.is_fov = False
        self.block_chain.clear()
        self.capacity = random.choice(CAPACITY)  # 计算能力
        self.transrate = random.choice(TRANS_RATE)  # 到rsu传输速率
        self.reputation = 100  # 声誉
