import numpy as np

from .block import Block
from .vehicle import Vehicle
from .config import *


class RSU:
    def __init__(self, rid):
        self.rid = rid
        self._block_interval = 1
        self._block_size = 100
        self._block_count = 0
        self.block_chain = []
        self.vehicles = []
        self.fov = None
        self.transactions = []
        self.transaction_mean_size = MIN_TRANSACTION_SIZE

    @property
    def block_interval(self):
        return self._block_interval

    @property
    def block_size(self):
        return self._block_size

    @property
    def norm_transaction_size(self):
        return self.transaction_mean_size / MAX_TRANSACTION_SIZE
    
    @property
    def vector(self):
        return np.hstack([self.norm_transaction_size, len(self.vehicles)])
    
    def set_block_size(self, block_size):
        self._block_size = block_size

    def set_block_interval(self, block_interval):
        self._block_interval = block_interval

    def add_vehicle(self, vehicle: Vehicle):
        if not self.fov:
            self.fov = vehicle
        self.vehicles.append(vehicle)

    def rsu_set_fov(self, fov: Vehicle):
        if self.fov:
            self.fov.set_fov(False)
        if fov in self.vehicles:
            self.fov = fov
            self.fov.set_fov(True)
        else:
            raise ValueError("FOV not in vehicles")

    def rsu_generate_transaction(self):
        if not self.fov:
            raise ValueError("FOV not set")
        trans, lantacy = self.fov.generate_transaction()
        # self.reputation_control(trans)
        # self.transactions.append(trans)
        return trans, lantacy

    def generate_block(self):
        self._block_count += 1
        interval = 0
        size = 0
        gen_latency = 0
        new_block = Block()
        # 车辆以柏松分布产生事务
        transaction_num = int(np.random.poisson(MEAN_TRANSACTION_NUM))
        for _ in range(transaction_num):
            t, latency = self.rsu_generate_transaction()
            self.transactions.append(t)
            gen_latency += latency
            if gen_latency > self._block_interval:
                break
        while size < self._block_size:
            if not self.transactions:
                break
            t = self.transactions.pop(0)
            size += t.size
            new_block.add_transaction(t)
        new_block.set_size(size)
        # 向所属vehicle发送区块
        send_latency = self.send_block(new_block)
        # 返回生成和发送区块时延
        return new_block, gen_latency, send_latency
    # fov向RSU发送区块
    def send_block(self, block):
        latency = block.size / self.fov.transrate
        # 返回最长发送时延
        return latency

    # todo 这东西还没完善,现在基本没用
    # def reputation_control(self, trans):
    #     if trans.is_fake:
    #         self.fov.reputation -= 5
    #     else:
    #         self.fov.reputation += 3

    def calculate_reward(self, block, gen_latency, send_latency, plently):
        # throughput = len(block.transactions) / (gen_latency + send_latency)
        throughput = len(block.transactions) / self._block_interval
        # print("{},{},{},{}".format(throughput, plently, gen_latency, send_latency))
        reward = throughput * THROUGHPUT_COEF - (gen_latency + send_latency) * LATENCY_COEF - plently
        # print("reward:", reward, "throughput:", throughput, "latency:", gen_latency+send_latency)

        return reward, throughput

    def operate(self, fov: Vehicle, block_size, block_interval):
        self.rsu_set_fov(fov)
        self.set_block_size(block_size)
        self.set_block_interval(block_interval)

        block, gen_latency, send_latency = self.generate_block()

        if block.transactions:
            self.transaction_mean_size = block.size / len(block.transactions)
        self.block_chain.append(block)

        # 当区块未容纳所有事务时，奖励为0
        plently = 0
        if self.transactions:
            plently = len(self.transactions)
            self.transactions.clear()

        reward, throughput = self.calculate_reward(block, gen_latency, send_latency, plently)
        return reward, throughput

    def reset(self):
        self._block_count = 0
        self.block_chain.clear()
        self.fov = self.rsu_set_fov(np.random.choice(self.vehicles))
        self.transaction_mean_size = MIN_TRANSACTION_SIZE


