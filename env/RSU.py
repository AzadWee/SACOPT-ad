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
        self.local_chain = []
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
        return np.hstack(([v.norm_capacity for v in self.vehicles], [v.norm_transrate for v in self.vehicles]))
    
    def set_block_size(self, block_size):
        self._block_size = block_size

    def set_block_interval(self, block_interval):
        self._block_interval = block_interval

    def add_vehicle(self, vehicle: Vehicle):
        if not self.fov:
            self.fov = vehicle
        self.vehicles.append(vehicle)

    def rsu_set_fov(self, fov_id:int):
        if self.fov:
            self.fov.set_fov(False)
        self.fov = self.vehicles[fov_id]
        self.fov.set_fov(True)

    def generate_block(self):
        self._block_count += 1
        gen_latency = 0
        
        # 生成区块(打包)
        new_block = Block(self._block_size)
        gen_latency = self.fov.generate_block(new_block)
        # 向所属vehicle发送区块（共识）
        send_latency = self.consensus_block(new_block)
        # 返回生成和发送区块时延
        return new_block, gen_latency, send_latency
    
    # fov向RSU发送区块,返回值为共识时延
    def consensus_block(self, block: Block):
        # 返回最长发送时延
        latency = 0
        for vehicle in self.vehicles:
            if vehicle == self.fov:
                continue
            latency = max(latency, vehicle.upload_block(block))
        return latency


    def calculate_reward(self, block:Block, gen_latency, send_latency):
        # 
        if gen_latency + send_latency > self.interval_factor * self._block_interval:
            return 0
        throughput = block.size / self._block_interval
        # print("{},{},{},{}".format(throughput, plently, gen_latency, send_latency))
        # print("reward:", reward, "throughput:", throughput, "latency:", gen_latency+send_latency)

        return throughput

    def operate(self, fov_id:int, block_size:int, block_interval:int, is_generate:bool):
        assert fov_id < len(self.vehicles), \
            "FOV id should be less than the number of vehicles"
        
        self.rsu_set_fov(fov_id)
        self.set_block_size(block_size)
        self.set_block_interval(block_interval)

        # 头车生成新的区块
        if is_generate:
            # gen_latency为生成区块时延，send_latency为区块内共识时延
            block, gen_latency, send_latency = self.generate_block()
            # fov将区块上传到RSU，delivery_latency为上传时延
            delivery_latency = self.fov.upload_block(block)
            self.local_chain.append(block)
        else:
            block = None
            gen_latency = 0
            send_latency = 0
            delivery_latency = 0
        # reward = self.calculate_reward(block, gen_latency, send_latency)
        delay = gen_latency + delivery_latency + send_latency
        return block, delay

    def reset(self):
        self._block_count = 0
        self.local_chain.clear()
        self.fov = self.vehicles[0]
        self.transaction_mean_size = MIN_TRANSACTION_SIZE
