import numpy as np

from .config import *
from .vehicle import Vehicle
from .RSU import RSU
from .block import Block


class Manager:
    def __init__(self):
        self._n_vehicle = VEHICLE_NUMBER
        self._n_rsu = RSU_NUMBER
        self._n_shard = VEHICLE_NUMBER // RSU_NUMBER
        self._vehicles = [Vehicle(vid, vid // self._n_shard) for vid in range(VEHICLE_NUMBER)]
        self.global_chain = []
        self._rsu = [RSU(rid) for rid in range(RSU_NUMBER)]
        for r in self._rsu:
            for v in self._vehicles:
                if v.rid == r.rid:
                    r.add_vehicle(v)
        self.is_generate_mask = np.zeros(self._n_rsu) # 用于判断哪些分片生成区块
        self.global_step = 0
        self.interval_factor = INTERVAL_FACTOR

    @property
    def good_vehicles(self):
        return self._vehicles

    @property
    def rsu(self):
        return self._rsu

    @property
    def space_vector(self):
        '''状态空间为车辆处理能力+传输时延'''
        vec = self._rsu[0].vector
        # vec += [r.vector for r in self._rsu]
        return np.hstack(vec)
    
    def capacity_change(self):
        indices = {capacity: i for i, capacity in enumerate(CAPACITY)}

        for v in self._rsu[0].vehicles:
            current_capacity = v.capacity
            current_index = indices[current_capacity]
            new_capacity = np.random.choice(CAPACITY, p=TRANSITION_MATRIX_1[current_index])
            v.change_capacity(new_capacity)
        for r in self._rsu[1:]:
            for i,v in enumerate(r.vehicles):
                v.change_capacity(self._rsu[0].vehicles[i].capacity)

    def transrate_change(self):
        indices = {rate: i for i, rate in enumerate(TRANS_RATE)}
        for v in self._rsu[0].vehicles:
            current_rate = v.transrate
            current_index = indices[current_rate]
            new_rate = np.random.choice(TRANS_RATE, p=TRANSITION_MATRIX_2[current_index])
            v.change_transrate(new_rate)
        for r in self._rsu[1:]:
            for i,v in enumerate(r.vehicles):
                v.change_transrate(self._rsu[0].vehicles[i].transrate)
    
    def is_generate_block(self):
        '''随机确定哪些分片生成区块，结果存储在is_generate_mask中，1表示生成区块，0表示不生成区块'''
        is_vehicle_generate = np.random.randint(2, size=self._n_vehicle)
        vehicle_ids = np.where(is_vehicle_generate == 1)[0]
        self.is_generate_mask = np.zeros(self._n_rsu)
        for vid in vehicle_ids:
            self.is_generate_mask[self._vehicles[vid].rid] = 1
            
    #todo: 奖励计算方法需要更改
    def calculate_reward(self, throughput, delay, block_interval):        
        if delay > self.interval_factor * block_interval:
            return 0
        else:
            return throughput
        
    def set(self, action, global_step):
        '''action包括头车选择,区块大小,区块间隔'''
        # action一维为fov，二维为区块大小，三维为区块间隔
        fov_id = action // (BLOCK_SIZE_RANGE * BLOCK_INTERVAL_RANGE)
        block_size = (action // BLOCK_INTERVAL_RANGE) % BLOCK_SIZE_RANGE + MIN_BLOCK_SIZE
        block_interval = action % BLOCK_INTERVAL_RANGE + MIN_BLOCK_INTERVAL


        # print("action:{},{},{}".format(fov_id, block_size, block_interval))

        assert MIN_BLOCK_SIZE <= block_size <= MAX_BLOCK_SIZE, \
            "Block size should be in the range of [{}, {}]".format(MIN_BLOCK_SIZE, MAX_BLOCK_SIZE)
        assert MIN_BLOCK_INTERVAL <= block_interval <= MAX_BLOCK_INTERVAL, \
            "Block interval should be in the range of [{}, {}]".format(MIN_BLOCK_INTERVAL, MAX_BLOCK_INTERVAL)

        
        # 随机生成is_generate_mask
        self.is_generate_block()
        
        # 求每个分片中最大处理时间和最大共识时间
        
        max_delay = 0
        big_block = Block()
        # 每个RSU(分片)进行操作
        for r in self._rsu:
            block, delay = r.operate(fov_id, block_size, block_interval, self.is_generate_mask[r.rid])
            max_delay = max(max_delay, delay)
            if block:
                big_block.set_size(big_block.size + block.size)
        self.global_chain.append(big_block)
            
        throughput = np.sum(self.is_generate_mask) * block_size / block_interval
        # throughput = block_size / block_interval
        reward = self.calculate_reward(throughput, max_delay, block_interval)
        print("throughput:{}, delay:{}, interval{}, reward:{}".format(throughput, max_delay, block_interval, reward))

        self.global_step += 1

        # 每隔一段时间改变传输速率和处理能力
        if self.global_step % 5 == 0:
            self.transrate_change()
            self.capacity_change()

        return reward, throughput
    
    @property
    def best_action(self):
        '''最优动作为选择处理能力最大的车辆作为FOV，区块大小为最大值，区块间隔为最小值'''
        max_capacity = 0
        fov = None
        for v in self._vehicles:
            if v.capacity > max_capacity:
                max_capacity = v.capacity
                fov = v
        return fov.vid * BLOCK_SIZE_RANGE * BLOCK_INTERVAL_RANGE

    def reset(self):
        for v in self._vehicles:
            v.reset()
        for r in self._rsu:
            r.reset()
        self.global_chain.clear()
        self.is_generate_mask = np.zeros(self._n_rsu)
        self.global_step = 0
        return self.space_vector
