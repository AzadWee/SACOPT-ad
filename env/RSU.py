from numpy import random

from .block import Block
from .vehicle import Vehicle
from .config import THROUGHPUT_COEF, LATENCY_COEF


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
        self.transaction_mean_size = 50

    @property
    def block_interval(self):
        return self._block_interval

    @property
    def block_size(self):
        return self._block_size

    @property
    def transaction_size(self):
        return self.transaction_mean_size

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
        self.reputation_control(trans)
        # self.transactions.append(trans)
        return trans, lantacy

    def generate_block(self):
        self._block_count += 1
        interval = 0
        size = 0
        gen_latency = 0
        new_block = Block()
        # for i in range(len(self.transactions)):
        #     if size > self._block_size:
        #         break
        #     t = self.transactions.pop(i)
        #     size += t.size
        #     new_block.add_transaction(t)
        while size < self._block_size and interval < self._block_interval:
            t, latency = self.rsu_generate_transaction()
            size += t.size
            gen_latency += latency
            new_block.add_transaction(t)
            # todo 这里的interval只考虑了生成事务的时间，没有考虑传输时间
            interval += latency
        new_block.set_size(size)
        # 向所属vehicle发送区块
        send_latency = self.send_block(new_block)
        # 返回生成和发送区块时延
        return new_block, gen_latency, send_latency

    def send_block(self, block):
        latency = 0
        # 返回最长发送时延
        for v in self.vehicles:
            v.add_block(block)
            if block.size / v.transrate > latency:
                latency = block.size / v.transrate
        return latency

    # todo 这东西还没完善,现在基本没用
    def reputation_control(self, trans):
        if trans.is_fake:
            self.fov.reputation -= 5
        else:
            self.fov.reputation += 3

    def calculate_reward(self, block, gen_latency, send_latency):
        # throughput = len(block.transactions) / (gen_latency + send_latency)
        throughput = len(block.transactions) / self._block_interval
        reward = throughput * THROUGHPUT_COEF - gen_latency * LATENCY_COEF
        # print("reward:", reward, "throughput:", throughput, "gen_latency:", gen_latency)

        return reward

    def operate(self, fov: Vehicle):
        self.rsu_set_fov(fov)
        # self._block_size = block_size
        # self._block_interval = block_interval
        block, gen_latency, send_latency = self.generate_block()

        self.transaction_mean_size = block.size / len(block.transactions)
        self.block_chain.append(block)

        reward = self.calculate_reward(block, gen_latency, send_latency)
        return reward

    def reset(self):
        self._block_count = 0
        self.block_chain.clear()
        self.fov = self.rsu_set_fov(random.choice(self.vehicles))
        self.transaction_mean_size = random.randint(40, 60)


